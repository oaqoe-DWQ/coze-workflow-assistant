"""
飞书机器人 + Coze 工作流集成
功能：接收飞书群消息 -> 提取文档链接 -> 触发 Coze 工作流 -> 发送完成消息
"""

import json
import logging
import threading
from flask import Flask, request, jsonify

# 导入配置和工具模块
import config
from utils import (
    extract_doc_url,
    build_rich_text_message,
    send_feishu_message,
    is_mention_bot,
    get_message_content,
    get_chat_id,
    logger
)

# 导入 Coze SDK
from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType, COZE_CN_BASE_URL

# 创建 Flask 应用
app = Flask(__name__)

# 初始化 Coze 客户端
coze_client = Coze(
    auth=TokenAuth(token=config.COZE_API_TOKEN),
    base_url=config.COZE_API_BASE
)

# 用于记录已处理的消息，避免重复处理
processed_messages = set()


def handle_workflow_stream(
    workflow_id: str,
    doc_url: str,
    chat_id: str
):
    """
    处理 Coze 工作流的流式响应
    
    Args:
        workflow_id: 工作流 ID
        doc_url: 文档链接
        chat_id: 飞书群组 ID
    """
    try:
        logger.info(f"开始调用工作流: workflow_id={workflow_id}, doc_url={doc_url}")
        
        # 收集工作流的输出结果
        workflow_results = []
        
        # 调用工作流（流式）
        stream = coze_client.workflows.runs.stream(
            workflow_id=workflow_id,
            parameters={
                "doc_url": doc_url
            }
        )
        
        # 处理流式事件
        for event in stream:
            if event.event == WorkflowEventType.MESSAGE:
                # 收到消息事件
                message = event.message
                logger.info(f"工作流消息: {message}")
                if message:
                    workflow_results.append(str(message))
                    
            elif event.event == WorkflowEventType.ERROR:
                # 收到错误事件
                error = event.error
                logger.error(f"工作流错误: {error}")
                workflow_results.append(f"错误: {error}")
                
            elif event.event == WorkflowEventType.INTERRUPT:
                # 收到中断事件（需要人工干预）
                logger.warning(f"工作流中断: {event.interrupt}")
                workflow_results.append("工作流需要人工干预")
        
        # 工作流执行完成，构建结果消息
        result_text = "\n".join(workflow_results) if workflow_results else "工作流执行完成"
        
        logger.info(f"工作流执行完成，结果: {result_text}")
        
        # 构建富文本消息卡片
        message_card = build_rich_text_message(
            doc_url=doc_url,
            workflow_result=result_text,
            status="success"
        )
        
        # 发送消息到飞书群
        success = send_feishu_message(chat_id, message_card)
        
        if success:
            logger.info(f"成功发送完成消息到群组: {chat_id}")
        else:
            logger.error(f"发送完成消息失败: chat_id={chat_id}")
            
    except Exception as e:
        logger.error(f"处理工作流时发生异常: {str(e)}")
        
        # 发送错误消息到群组
        try:
            error_card = build_rich_text_message(
                doc_url=doc_url,
                workflow_result=f"执行异常: {str(e)}",
                status="error"
            )
            send_feishu_message(chat_id, error_card)
        except Exception as send_error:
            logger.error(f"发送错误消息失败: {str(send_error)}")


def process_message_async(event_data: dict):
    """
    异步处理消息（在后台线程中执行）
    
    Args:
        event_data: 飞书事件数据
    """
    try:
        # 检查是否 @了机器人
        if not is_mention_bot(event_data):
            logger.info("消息未 @ 机器人，忽略")
            return
        
        # 获取消息内容
        message_content = get_message_content(event_data)
        if not message_content:
            logger.warning("无法提取消息内容")
            return
        
        logger.info(f"收到消息内容: {message_content}")
        
        # 提取文档链接
        doc_url = extract_doc_url(message_content)
        if not doc_url:
            logger.warning("消息中未找到文档链接")
            return
        
        # 获取群组 ID
        chat_id = get_chat_id(event_data)
        if not chat_id:
            logger.error("无法获取 chat_id")
            return
        
        logger.info(f"准备处理文档: {doc_url}, 群组: {chat_id}")
        
        # 调用工作流处理
        handle_workflow_stream(
            workflow_id=config.COZE_WORKFLOW_ID,
            doc_url=doc_url,
            chat_id=chat_id
        )
        
    except Exception as e:
        logger.error(f"异步处理消息时发生异常: {str(e)}")


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    飞书事件回调接口
    """
    try:
        # 获取请求数据
        data = request.json
        
        # 日志记录
        logger.info(f"收到飞书回调: {json.dumps(data, ensure_ascii=False)}")
        
        # 1. 处理 URL 验证（challenge）
        if 'challenge' in data:
            challenge = data['challenge']
            logger.info(f"收到 challenge 验证: {challenge}")
            return jsonify({"challenge": challenge})
        
        # 2. 验证 Token
        token = data.get('header', {}).get('token')
        if token != config.FEISHU_VERIFICATION_TOKEN:
            logger.warning(f"Token 验证失败: {token}")
            return jsonify({"error": "invalid token"}), 401
        
        # 3. 处理事件
        event_type = data.get('header', {}).get('event_type')
        
        if event_type == 'im.message.receive_v1':
            # 接收到消息事件
            event_data = data.get('event', {})
            
            # 获取消息 ID，用于去重
            message_id = event_data.get('message', {}).get('message_id')
            
            # 检查是否已处理过
            if message_id in processed_messages:
                logger.info(f"消息已处理过，跳过: {message_id}")
                return jsonify({"message": "already processed"})
            
            # 标记为已处理
            processed_messages.add(message_id)
            
            # 在后台线程中处理消息（避免阻塞回调响应）
            thread = threading.Thread(
                target=process_message_async,
                args=(event_data,)
            )
            thread.daemon = True
            thread.start()
            
            logger.info(f"已启动后台线程处理消息: {message_id}")
            
        else:
            logger.info(f"收到其他类型事件: {event_type}")
        
        # 返回成功响应
        return jsonify({"message": "success"})
        
    except Exception as e:
        logger.error(f"处理 webhook 时发生异常: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """
    健康检查接口
    """
    return jsonify({
        "status": "ok",
        "service": "飞书机器人 + Coze 工作流",
        "version": "1.0.0"
    })


@app.route('/', methods=['GET'])
def index():
    """
    根路径，显示服务信息
    """
    return """
    <h1>飞书机器人 + Coze 工作流集成服务</h1>
    <p>服务运行中...</p>
    <ul>
        <li>Webhook 地址: /webhook</li>
        <li>健康检查: /health</li>
    </ul>
    """


def main():
    """
    主函数，启动 Flask 服务
    """
    logger.info("=" * 60)
    logger.info("飞书机器人 + Coze 工作流集成服务启动中...")
    logger.info(f"监听地址: {config.FLASK_HOST}:{config.FLASK_PORT}")
    logger.info(f"Webhook 路径: http://{config.FLASK_HOST}:{config.FLASK_PORT}/webhook")
    logger.info("=" * 60)
    
    # 启动 Flask 应用
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == '__main__':
    main()


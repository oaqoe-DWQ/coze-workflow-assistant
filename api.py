"""
简化版后端 API - 只提供文档处理接口
无需飞书事件订阅，通过前端页面触发
"""

import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入配置和工具模块
import config
from utils import (
    extract_doc_url,
    build_rich_text_message,
    send_via_custom_bot_webhook,
    logger
)

# 导入 Coze SDK
from cozepy import Coze, TokenAuth, WorkflowEvent, WorkflowEventType

# 创建 Flask 应用
app = Flask(__name__)

# 启用 CORS（允许前端跨域请求）
CORS(app)

# 初始化 Coze 客户端
coze_client = Coze(
    auth=TokenAuth(token=config.COZE_API_TOKEN),
    base_url=config.COZE_API_BASE
)


def process_workflow(doc_url: str) -> dict:
    """
    处理 Coze 工作流（流式调用）
    
    Args:
        doc_url: 文档链接
    
    Returns:
        包含处理结果的字典
    """
    try:
        logger.info(f"开始调用工作流: doc_url={doc_url}")
        
        # 存储工作流结果
        workflow_messages = []  # 所有消息
        workflow_output = None  # 最终输出变量
        workflow_data = {}  # 工作流数据
        
        # 构建调用参数
        params = {
            "workflow_id": config.COZE_WORKFLOW_ID,
            "parameters": {
                "inputurl": doc_url  # 使用 inputurl 参数名
            }
        }
        
        # 添加 bot_id（如果配置了）
        if hasattr(config, 'COZE_BOT_ID') and config.COZE_BOT_ID:
            params["bot_id"] = config.COZE_BOT_ID
            logger.info(f"使用 Bot ID: {config.COZE_BOT_ID}")
        
        logger.info(f"调用参数: {params}")
        
        # 开始流式调用
        stream = coze_client.workflows.runs.stream(**params)
        
        logger.info("开始监听工作流事件流...")
        
        # 处理流式事件
        for event in stream:
            event_type = event.event
            logger.info(f"收到事件: {event_type}")
            
            # MESSAGE 事件 - 工作流执行过程中的消息
            if event_type == WorkflowEventType.MESSAGE:
                message = event.message
                logger.info(f"MESSAGE 内容: {message}")
                if message:
                    workflow_messages.append(str(message))
            
            # ERROR 事件 - 工作流执行错误
            elif event_type == WorkflowEventType.ERROR:
                error = event.error
                logger.error(f"ERROR: {error}")
                return {
                    "success": False,
                    "error": str(error)
                }
            
            # INTERRUPT 事件 - 工作流中断，需要恢复
            elif event_type == WorkflowEventType.INTERRUPT:
                logger.info(f"INTERRUPT: {event.interrupt}")
                interrupt_data = event.interrupt.interrupt_data
                
                # 自动恢复执行
                logger.info("自动恢复工作流执行...")
                resume_stream = coze_client.workflows.runs.resume(
                    workflow_id=config.COZE_WORKFLOW_ID,
                    event_id=interrupt_data.event_id,
                    resume_data="",
                    interrupt_type=interrupt_data.type
                )
                
                # 递归处理恢复后的事件
                for resume_event in resume_stream:
                    if resume_event.event == WorkflowEventType.MESSAGE:
                        if resume_event.message:
                            workflow_messages.append(str(resume_event.message))
                    elif resume_event.event == WorkflowEventType.ERROR:
                        return {"success": False, "error": str(resume_event.error)}
            
            # 其他事件类型，记录用于调试
            else:
                logger.info(f"其他事件类型: {event_type}")
                # 记录完整事件以便调试
                logger.info(f"完整事件对象: {event}")
                
                # 尝试提取事件中的数据
                if hasattr(event, '__dict__'):
                    logger.info(f"事件属性: {event.__dict__}")
        
        logger.info("✅ 工作流事件流结束")
        
        # 提取最终输出
        import re
        # 定义匹配 output 的正则表达式模式
        patterns = [
            r'"output"\s*:\s*"([^"]+)"',
            r'output\s*:\s*"([^"]+)"',
            r'output\s*:\s*([^\s\n,\}]+)',
        ]
        
        # 方法1: 从最后一个消息中提取（很多工作流会在最后输出结果）
        if workflow_messages:
            last_message = workflow_messages[-1]
            logger.info(f"最后一条消息: {last_message}")
            
            # 尝试从消息中提取 output
            for pattern in patterns:
                match = re.search(pattern, last_message)
                if match:
                    workflow_output = match.group(1)
                    logger.info(f"✅ 从最后一条消息中提取到 output: {workflow_output}")
                    break
        
        # 方法2: 如果还是没有提取到，检查所有消息
        if not workflow_output and workflow_messages:
            full_text = "\n".join(workflow_messages)
            logger.info(f"尝试从完整文本中提取 output...")
            for pattern in patterns:
                match = re.search(pattern, full_text)
                if match:
                    workflow_output = match.group(1)
                    logger.info(f"✅ 从完整文本中提取到 output: {workflow_output}")
                    break
        
        # 添加 URL 协议前缀
        if workflow_output and not workflow_output.startswith(('http://', 'https://')):
            workflow_output = f"http://{workflow_output}"
            logger.info(f"添加协议后: {workflow_output}")
        
        # 构建返回结果
        result_text = "\n".join(workflow_messages) if workflow_messages else "工作流执行完成"
        
        logger.info(f"最终结果文本: {result_text}")
        logger.info(f"最终输出链接: {workflow_output}")
        
        return {
            "success": True,
            "result": result_text,
            "output": workflow_output
        }
        
    except Exception as e:
        logger.error(f"处理工作流时发生异常: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


@app.route('/api/process', methods=['POST'])
def api_process():
    """
    处理文档的 API 接口
    """
    try:
        # 获取请求数据
        data = request.json
        
        if not data or 'doc_url' not in data:
            return jsonify({
                "success": False,
                "message": "缺少 doc_url 参数"
            }), 400
        
        doc_url = data['doc_url'].strip()
        
        # 验证链接格式
        if not extract_doc_url(doc_url):
            return jsonify({
                "success": False,
                "message": "无效的飞书文档链接"
            }), 400
        
        logger.info(f"收到处理请求: {doc_url}")
        
        # 调用工作流处理
        result = process_workflow(doc_url)
        
        if result['success']:
            # 构建富文本消息卡片
            message_card = build_rich_text_message(
                doc_url=doc_url,
                workflow_result=result.get('result', '工作流执行完成'),
                workflow_output=result.get('output'),  # 传递输出链接
                status="success"
            )
            
            # 通过 Webhook 发送消息到飞书群
            send_success = send_via_custom_bot_webhook(message_card)
            
            if send_success:
                logger.info("成功发送完成消息到飞书群")
            else:
                logger.warning("发送完成消息失败")
            
            return jsonify({
                "success": True,
                "message": "工作流已触发，处理完成后将在飞书群内收到通知",
                "result": result.get('result')
            })
        else:
            # 发送错误消息
            error_card = build_rich_text_message(
                doc_url=doc_url,
                workflow_result=f"执行失败: {result.get('error', '未知错误')}",
                status="error"
            )
            send_via_custom_bot_webhook(error_card)
            
            return jsonify({
                "success": False,
                "message": result.get('error', '工作流执行失败')
            }), 500
            
    except Exception as e:
        logger.error(f"API 处理异常: {str(e)}")
        return jsonify({
            "success": False,
            "message": f"服务器错误: {str(e)}"
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """
    健康检查接口
    """
    return jsonify({
        "status": "ok",
        "service": "Coze 工作流助手 API",
        "version": "2.0.0"
    })


@app.route('/', methods=['GET'])
def index():
    """
    API 根路径
    """
    return jsonify({
        "message": "Coze 工作流助手 API",
        "version": "2.0.0",
        "endpoints": {
            "process": "/api/process (POST)",
            "health": "/api/health (GET)"
        }
    })


def main():
    """
    主函数，启动 Flask 服务
    """
    logger.info("=" * 60)
    logger.info("Coze 工作流助手 API 启动中...")
    logger.info(f"监听地址: {config.FLASK_HOST}:{config.FLASK_PORT}")
    logger.info(f"API 端点: http://{config.FLASK_HOST}:{config.FLASK_PORT}/api/process")
    logger.info("=" * 60)
    
    # 启动 Flask 应用
    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG
    )


if __name__ == '__main__':
    main()


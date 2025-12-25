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
    处理 Coze 工作流
    
    Args:
        doc_url: 文档链接
    
    Returns:
        包含处理结果的字典
    """
    try:
        logger.info(f"开始调用工作流: doc_url={doc_url}")
        
        # 收集工作流的输出结果
        workflow_results = []
        
        # 调用工作流（流式）
        stream = coze_client.workflows.runs.stream(
            workflow_id=config.COZE_WORKFLOW_ID,
            parameters={
                "inputurl": doc_url
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
                return {
                    "success": False,
                    "error": str(error)
                }
                
            elif event.event == WorkflowEventType.INTERRUPT:
                # 收到中断事件
                logger.warning(f"工作流中断: {event.interrupt}")
                workflow_results.append("工作流需要人工干预")
        
        # 工作流执行完成
        result_text = "\n".join(workflow_results) if workflow_results else "工作流执行完成"
        
        logger.info(f"工作流执行完成，结果: {result_text}")
        
        return {
            "success": True,
            "result": result_text
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


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
        workflow_output = None  # 存储工作流的输出变量
        workflow_completed = False
        
        # 调用工作流（流式）
        stream = coze_client.workflows.runs.stream(
            workflow_id=config.COZE_WORKFLOW_ID,
            parameters={
                "inputurl": doc_url
            }
        )
        
        # 处理流式事件
        logger.info("开始监听工作流事件流...")
        event_count = 0
        for event in stream:
            event_count += 1
            logger.info(f"收到事件 [{event_count}]: {event.event}")
            
            if event.event == WorkflowEventType.MESSAGE:
                # 收到消息事件
                message = event.message
                logger.info(f"工作流消息内容: {message}")
                if message:
                    workflow_results.append(str(message))
                
                # 尝试提取输出变量（工作流完成时会包含输出）
                if hasattr(event, 'data') and event.data:
                    logger.info(f"事件数据: {event.data}")
                    if isinstance(event.data, dict) and 'output' in event.data:
                        workflow_output = event.data.get('output')
                        logger.info(f"✅ 提取到输出变量: {workflow_output}")
                    
            elif event.event == WorkflowEventType.ERROR:
                # 收到错误事件
                error = event.error
                logger.error(f"工作流错误: {error}")
                return {
                    "success": False,
                    "error": str(error)
                }
                
            elif event.event == WorkflowEventType.INTERRUPT:
                # 收到中断事件，需要继续执行
                logger.info(f"工作流中断，准备恢复执行: {event.interrupt}")
                
                # 获取中断信息
                interrupt_data = event.interrupt.interrupt_data
                event_id = interrupt_data.event_id
                interrupt_type = interrupt_data.type
                
                logger.info(f"中断类型: {interrupt_type}, Event ID: {event_id}")
                
                # 调用 resume 继续执行工作流
                try:
                    logger.info("调用 resume 接口继续执行工作流...")
                    resume_stream = coze_client.workflows.runs.resume(
                        workflow_id=config.COZE_WORKFLOW_ID,
                        event_id=event_id,
                        resume_data="continue",  # 继续执行
                        interrupt_type=interrupt_type
                    )
                    
                    # 处理恢复后的流式事件
                    resume_message_count = 0
                    for resume_event in resume_stream:
                        if resume_event.event == WorkflowEventType.MESSAGE:
                            message = resume_event.message
                            logger.info(f"恢复后的消息 [{resume_message_count + 1}]: {message}")
                            if message:
                                workflow_results.append(str(message))
                                resume_message_count += 1
                        elif resume_event.event == WorkflowEventType.ERROR:
                            error = resume_event.error
                            logger.error(f"恢复后出错: {error}")
                            return {
                                "success": False,
                                "error": str(error)
                            }
                        else:
                            # 记录其他类型的事件
                            logger.info(f"恢复后收到事件: {resume_event.event}")
                    
                    logger.info(f"✅ 工作流恢复执行完成，收到 {resume_message_count} 条消息")
                    
                except Exception as resume_error:
                    logger.error(f"恢复工作流时出错: {str(resume_error)}")
                    workflow_results.append(f"工作流恢复失败: {str(resume_error)}")
            
            else:
                # 记录其他类型的事件（用于调试）
                logger.info(f"收到其他类型事件: {event.event}")
        
        # 流式事件循环结束，表示工作流已完成
        workflow_completed = True
        logger.info("✅ 工作流事件流已结束，工作流执行完成")
        
        # 检查是否有结果
        if not workflow_results:
            logger.warning("工作流执行完成，但未收到任何输出消息")
            result_text = "工作流执行完成（无输出结果）"
        else:
            result_text = "\n".join(workflow_results)
            logger.info(f"工作流执行完成，共收到 {len(workflow_results)} 条消息")
        
        # 如果有输出变量，添加到结果中
        if workflow_output:
            logger.info(f"✅ 工作流输出变量: {workflow_output}")
            # 如果 output 是链接，添加协议前缀
            if workflow_output and not workflow_output.startswith(('http://', 'https://')):
                workflow_output = f"http://{workflow_output}"
                logger.info(f"添加协议前缀后: {workflow_output}")
        
        logger.info(f"最终结果: {result_text}")
        
        return {
            "success": True,
            "result": result_text,
            "output": workflow_output,  # 返回输出变量
            "completed": workflow_completed
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
                workflow_output=result.get('output'),  # 传递输出变量
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


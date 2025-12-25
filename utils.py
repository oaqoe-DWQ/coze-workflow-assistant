"""
工具模块 - 提供飞书 API 调用、消息构建等功能
"""

import re
import time
import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime

import config

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FeishuTokenManager:
    """飞书 Access Token 管理器，支持缓存"""
    
    def __init__(self):
        self._access_token = None
        self._token_expire_time = 0
    
    def get_tenant_access_token(self) -> Optional[str]:
        """
        获取租户访问令牌（tenant_access_token）
        如果缓存未过期则返回缓存的 token，否则重新获取
        """
        current_time = time.time()
        
        # 如果 token 未过期，直接返回
        if self._access_token and current_time < self._token_expire_time:
            return self._access_token
        
        # 重新获取 token
        url = f"{config.FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": config.FEISHU_APP_ID,
            "app_secret": config.FEISHU_APP_SECRET
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('code') == 0:
                self._access_token = data.get('tenant_access_token')
                # 设置过期时间（提前 5 分钟刷新）
                expire_in = data.get('expire', config.TOKEN_CACHE_DURATION)
                self._token_expire_time = current_time + expire_in - 300
                logger.info("成功获取飞书 tenant_access_token")
                return self._access_token
            else:
                logger.error(f"获取 token 失败: {data.get('msg')}")
                return None
                
        except Exception as e:
            logger.error(f"获取 tenant_access_token 异常: {str(e)}")
            return None


# 全局 token 管理器实例
token_manager = FeishuTokenManager()


def extract_doc_url(text: str) -> Optional[str]:
    """
    从文本中提取飞书文档链接
    
    支持的格式：
    - https://xxx.feishu.cn/docx/xxxxx
    - https://xxx.feishu.cn/wiki/xxxxx
    - https://xxx.feishu.cn/docs/xxxxx
    - https://xxx.feishu.cn/sheets/xxxxx
    - https://xxx.feishu.cn/base/xxxxx
    - https://xxx.larkoffice.com/docx/xxxxx
    
    Args:
        text: 待提取的文本
    
    Returns:
        提取到的文档链接，如果没有找到则返回 None
    """
    # 正则表达式匹配飞书文档链接
    pattern = r'https://[a-zA-Z0-9\-]+\.(feishu|larkoffice)\.(cn|com)/(?:docx|wiki|docs|sheets|base|file)/[a-zA-Z0-9\-_]+'
    
    match = re.search(pattern, text)
    if match:
        url = match.group(0)
        logger.info(f"提取到文档链接: {url}")
        return url
    
    logger.warning("未找到有效的飞书文档链接")
    return None


def build_rich_text_message(
    doc_url: str,
    workflow_result: str = None,
    workflow_output: str = None,
    status: str = "success"
) -> Dict[str, Any]:
    """
    构建飞书富文本消息卡片
    
    Args:
        doc_url: 原始文档链接
        workflow_result: 工作流处理结果
        workflow_output: 工作流输出链接
        status: 任务状态 (success/error)
    
    Returns:
        消息卡片 JSON 结构
    """
    # 使用中国时区（东八区 UTC+8）
    china_tz = timezone(timedelta(hours=8))
    current_time = datetime.now(china_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    # 根据状态设置颜色和文本
    if status == "success":
        status_text = "✅ 任务已完成"
        color = "green"
    else:
        status_text = "❌ 任务执行失败"
        color = "red"
    
    # 构建卡片元素
    elements = [
        {
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**{status_text}**"
            }
        },
        {
            "tag": "hr"
        }
    ]
    
    # 如果有输出链接，优先显示（最醒目）
    if workflow_output:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**🎉 生成结果:** [点击查看]({workflow_output})"
            }
        })
        elements.append({
            "tag": "hr"
        })
    
    # 显示原始文档
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**📄 原始文档:** [点击查看]({doc_url})"
        }
    })
    
    # 如果有工作流详细结果，添加（但不要太长）
    if workflow_result and len(workflow_result) < 300:
        elements.append({
            "tag": "div",
            "text": {
                "tag": "lark_md",
                "content": f"**📝 处理详情:**\n{workflow_result}"
            }
        })
    
    # 添加完成时间
    elements.append({
        "tag": "div",
        "text": {
            "tag": "lark_md",
            "content": f"**⏰ 完成时间:** {current_time}"
        }
    })
    
    # 构建完整消息卡片
    card = {
        "config": {
            "wide_screen_mode": True
        },
        "header": {
            "template": color,
            "title": {
                "tag": "plain_text",
                "content": "工作流执行通知"
            }
        },
        "elements": elements
    }
    
    return card


def send_feishu_message(
    chat_id: str,
    message_card: Dict[str, Any]
) -> bool:
    """
    发送飞书富文本消息卡片到指定群组
    支持两种方式：
    1. 使用自定义机器人 Webhook（如果配置了）
    2. 使用企业自建应用 API
    
    Args:
        chat_id: 群组 ID（使用 API 时需要，使用 Webhook 时可忽略）
        message_card: 消息卡片 JSON
    
    Returns:
        发送成功返回 True，否则返回 False
    """
    import json
    
    # 方式1：使用自定义机器人 Webhook
    if hasattr(config, 'USE_CUSTOM_BOT_WEBHOOK') and config.USE_CUSTOM_BOT_WEBHOOK:
        if hasattr(config, 'FEISHU_CUSTOM_BOT_WEBHOOK') and config.FEISHU_CUSTOM_BOT_WEBHOOK:
            return send_via_custom_bot_webhook(message_card)
    
    # 方式2：使用企业自建应用 API
    # 获取 access token
    access_token = token_manager.get_tenant_access_token()
    if not access_token:
        logger.error("无法获取 access_token，消息发送失败")
        return False
    
    # 构建发送消息的 URL
    url = f"{config.FEISHU_API_BASE}/im/v1/messages"
    
    # 构建请求头
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8"
    }
    
    # 构建请求体
    payload = {
        "receive_id": chat_id,
        "msg_type": "interactive",
        "content": json.dumps(message_card)
    }
    
    # 发送请求
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            params={"receive_id_type": "chat_id"},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 0:
            logger.info(f"消息发送成功（API）: message_id={data.get('data', {}).get('message_id')}")
            return True
        else:
            logger.error(f"消息发送失败（API）: {data.get('msg')}")
            return False
            
    except Exception as e:
        logger.error(f"发送消息异常（API）: {str(e)}")
        return False


def send_via_custom_bot_webhook(message_card: Dict[str, Any]) -> bool:
    """
    通过自定义机器人 Webhook 发送消息
    
    Args:
        message_card: 消息卡片 JSON
    
    Returns:
        发送成功返回 True，否则返回 False
    """
    import json
    
    webhook_url = config.FEISHU_CUSTOM_BOT_WEBHOOK
    
    # 构建 Webhook 请求体
    payload = {
        "msg_type": "interactive",
        "card": message_card
    }
    
    try:
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(payload),
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 0 or data.get('StatusCode') == 0:
            logger.info(f"消息发送成功（Webhook）")
            return True
        else:
            logger.error(f"消息发送失败（Webhook）: {data}")
            return False
            
    except Exception as e:
        logger.error(f"发送消息异常（Webhook）: {str(e)}")
        return False


def is_mention_bot(event_data: Dict[str, Any], bot_open_id: str = None) -> bool:
    """
    检查消息是否 @了机器人
    
    Args:
        event_data: 事件数据
        bot_open_id: 机器人的 open_id（可选，如果不提供则只检查 mentions 字段）
    
    Returns:
        如果消息 @了机器人返回 True，否则返回 False
    """
    try:
        message = event_data.get('message', {})
        mentions = message.get('mentions', [])
        
        # 如果没有 @任何人，返回 False
        if not mentions:
            return False
        
        # 如果提供了 bot_open_id，检查是否 @了该机器人
        if bot_open_id:
            for mention in mentions:
                if mention.get('id', {}).get('open_id') == bot_open_id:
                    return True
            return False
        else:
            # 如果没有提供 bot_open_id，只要有 @就返回 True
            return True
            
    except Exception as e:
        logger.error(f"检查 @ 机器人时出错: {str(e)}")
        return False


def get_message_content(event_data: Dict[str, Any]) -> Optional[str]:
    """
    从事件数据中提取消息内容
    
    Args:
        event_data: 事件数据
    
    Returns:
        消息文本内容，如果提取失败返回 None
    """
    try:
        import json
        
        message = event_data.get('message', {})
        content_str = message.get('content', '{}')
        content = json.loads(content_str)
        
        # 提取文本内容
        text = content.get('text', '')
        return text
        
    except Exception as e:
        logger.error(f"提取消息内容时出错: {str(e)}")
        return None


def get_chat_id(event_data: Dict[str, Any]) -> Optional[str]:
    """
    从事件数据中提取群组 ID
    
    Args:
        event_data: 事件数据
    
    Returns:
        群组 ID，如果提取失败返回 None
    """
    try:
        message = event_data.get('message', {})
        chat_id = message.get('chat_id')
        return chat_id
        
    except Exception as e:
        logger.error(f"提取 chat_id 时出错: {str(e)}")
        return None


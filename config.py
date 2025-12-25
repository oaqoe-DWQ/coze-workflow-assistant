"""
配置文件 - 存储所有配置信息
请根据您的实际情况填写以下配置项
"""

# ===== Coze 配置 =====
# 从 Coze 平台获取的 API Token（过期时间：2026-01-24）
COZE_API_TOKEN = 'pat_YxybptyPLdYvVpEkIdyQ656pigqf9ZBpP37FNSHNVQxOFoS6kW3NjiRj3zLxemWl'

# Coze 工作流 ID（从工作流的网址最后一段数字）
COZE_WORKFLOW_ID = '7561294254754365486'

# Coze API 基础 URL
COZE_API_BASE = 'https://api.coze.cn'


# ===== 飞书机器人配置 =====
# 飞书开放平台 - 应用凭证
# 登录 https://open.feishu.cn/app 获取以下信息

# 应用 App ID（用于接收消息事件）
FEISHU_APP_ID = 'cli_a9c667a2b03a9cda'

# 应用 App Secret（用于接收消息事件）
FEISHU_APP_SECRET = 'FMgoedZBtfchABNJHW7Z3dvbVHMGFwZD'

# Verification Token（用于验证事件回调）
FEISHU_VERIFICATION_TOKEN = 'YOUR_VERIFICATION_TOKEN'  # ⚠️ 请从飞书开放平台获取并替换

# 飞书 API 基础 URL
FEISHU_API_BASE = 'https://open.feishu.cn/open-apis'

# ===== 自定义机器人 Webhook（可选）=====
# 如果您想使用自定义机器人 Webhook 发送消息，请填写以下 URL
# 否则将使用企业自建应用的 API 发送消息
FEISHU_CUSTOM_BOT_WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/61e7e70d-4cfb-4fc5-b51a-8a0b33317f46'

# 是否使用自定义机器人 Webhook 发送消息（True/False）
USE_CUSTOM_BOT_WEBHOOK = True  # 设置为 True 使用 Webhook，False 使用 API


# ===== Flask 服务配置 =====
# Flask 服务监听的主机地址
FLASK_HOST = '0.0.0.0'

# Flask 服务监听的端口
FLASK_PORT = 5000

# 是否开启调试模式（生产环境请设置为 False）
FLASK_DEBUG = True


# ===== 其他配置 =====
# Access Token 缓存时间（秒），飞书 token 有效期为 2 小时
TOKEN_CACHE_DURATION = 7000

# 日志级别
LOG_LEVEL = 'INFO'


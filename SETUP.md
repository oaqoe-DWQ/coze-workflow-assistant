# 快速配置指南

根据您的飞书机器人类型，选择对应的配置方式：

## 🎯 您的情况：已有自定义机器人 Webhook

您提供的 Webhook URL：`https://open.feishu.cn/open-apis/bot/v2/hook/61e7e70d-4cfb-4fc5-b51a-8a0b33317f46`

这是一个**自定义机器人**，但自定义机器人**无法接收消息**。要实现完整功能，您需要：

### ✅ 推荐方案：混合使用

1. **创建企业自建应用**（用于接收消息）
2. **使用您现有的 Webhook**（用于发送消息）

---

## 📋 配置步骤

### 步骤 1：创建企业自建应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 点击「创建企业自建应用」
3. 填写应用名称（如：Coze工作流助手）
4. 创建完成

### 步骤 2：获取应用凭证

在应用详情页 → 「凭证与基础信息」，获取：
- **App ID**：例如 `cli_xxxxxxxxx`
- **App Secret**：例如 `xxxxxxxxxxxxx`
- **Verification Token**：例如 `xxxxxxxxxxxxx`

### 步骤 3：配置权限

在应用管理后台 → 「权限管理」，添加以下权限：

✅ 必选权限：
- `im:message` - 获取与发送单聊、群组消息

点击「保存」后，在「版本管理与发布」创建版本并发布。

### 步骤 4：填写 config.py

打开 `F:\AIcase\config.py`，填写以下内容：

```python
# 飞书企业自建应用配置（用于接收消息）
FEISHU_APP_ID = 'cli_xxxxxxxxx'  # 替换为您的 App ID
FEISHU_APP_SECRET = 'xxxxxxxxxxxxx'  # 替换为您的 App Secret
FEISHU_VERIFICATION_TOKEN = 'xxxxxxxxxxxxx'  # 替换为您的 Verification Token

# 自定义机器人 Webhook（用于发送消息）
FEISHU_CUSTOM_BOT_WEBHOOK = 'https://open.feishu.cn/open-apis/bot/v2/hook/61e7e70d-4cfb-4fc5-b51a-8a0b33317f46'
USE_CUSTOM_BOT_WEBHOOK = True  # 使用 Webhook 发送消息
```

### 步骤 5：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 6：启动 ngrok（本地开发）

在新终端窗口运行：

```bash
ngrok http 5000
```

会得到类似：`https://abc123.ngrok.io` 的 URL

### 步骤 7：配置事件订阅

1. 在飞书应用管理后台 → 「事件订阅」
2. 配置请求地址：`https://abc123.ngrok.io/webhook`
3. 添加订阅事件：`im.message.receive_v1`
4. 保存

### 步骤 8：启动服务

```bash
python AIcase.py
```

看到以下输出表示成功：

```
============================================================
飞书机器人 + Coze 工作流集成服务启动中...
监听地址: 0.0.0.0:5000
Webhook 路径: http://0.0.0.0:5000/webhook
============================================================
```

### 步骤 9：将机器人添加到群组

⚠️ **重要**：需要添加**两个机器人**到同一个群：

1. **自定义机器人**（您已有的，用于发送消息）
   - 在群设置 → 机器人 → 添加机器人 → 自定义机器人
   
2. **企业自建应用**（您刚创建的，用于接收消息）
   - 在群设置 → 机器人 → 添加机器人 → 搜索您的应用名称

### 步骤 10：测试

在群中发送：

```
@您的企业自建应用 https://xxx.feishu.cn/docx/xxxxx
```

流程：
1. 企业自建应用接收到消息
2. 触发 Coze 工作流处理
3. 通过自定义机器人 Webhook 发送完成通知

---

## 🔄 另一种方案：只用企业自建应用

如果您不想使用两个机器人，可以只使用企业自建应用：

### 修改 config.py

```python
USE_CUSTOM_BOT_WEBHOOK = False  # 不使用 Webhook，使用 API
```

### 添加权限

在应用管理后台 → 「权限管理」，添加：
- `im:message:send_as_bot` - 以应用的身份发消息

### 只添加一个机器人

只需要将企业自建应用添加到群组即可。

---

## ❓ 常见问题

### Q: 为什么需要两个机器人？

A: 因为：
- **自定义机器人**：只能发送消息，不能接收
- **企业自建应用**：既能接收也能发送

如果想用您现有的自定义机器人发送消息（配置更简单），就需要两个机器人配合。

### Q: 我只想用一个机器人可以吗？

A: 可以！设置 `USE_CUSTOM_BOT_WEBHOOK = False`，只使用企业自建应用即可。

### Q: 配置事件订阅时验证失败？

A: 确保：
1. ngrok 正在运行
2. 服务已启动（`python AIcase.py`）
3. URL 格式正确（包含 `/webhook`）

---

## 📞 需要帮助？

查看详细文档：
- 飞书开放平台：https://open.feishu.cn/document/home/index
- Coze 文档：https://www.coze.cn/docs

或查看完整的 `README.md` 文件。


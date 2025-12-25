# 飞书机器人 + Coze 工作流集成

这是一个将飞书机器人与 Coze 工作流集成的服务，实现以下功能：
1. 在飞书群中 @机器人并发送飞书文档链接
2. 自动触发 Coze 工作流处理文档
3. 工作流完成后，机器人在群内发送富文本完成消息

## 项目结构

```
F:\AIcase\
├── AIcase.py          # 主程序（Flask 服务器 + 事件处理）
├── config.py          # 配置文件
├── utils.py           # 工具函数（飞书 API、消息构建器等）
├── requirements.txt   # Python 依赖
└── README.md         # 使用说明（本文件）
```

## 安装步骤

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 配置飞书机器人

#### 2.1 创建飞书机器人应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 点击「创建企业自建应用」
3. 填写应用名称和描述
4. 创建完成后，进入应用详情页

#### 2.2 获取应用凭证

在应用详情页的「凭证与基础信息」中，获取以下信息：
- **App ID**
- **App Secret**
- **Verification Token**

将这些信息填入 `config.py` 文件的对应位置：

```python
FEISHU_APP_ID = 'YOUR_APP_ID'
FEISHU_APP_SECRET = 'YOUR_APP_SECRET'
FEISHU_VERIFICATION_TOKEN = 'YOUR_VERIFICATION_TOKEN'
```

#### 2.3 配置权限

在应用管理后台的「权限管理」中，添加以下权限：

- `im:message` - 获取与发送单聊、群组消息
- `im:message:send_as_bot` - 以应用的身份发消息

添加权限后，需要在「版本管理与发布」中创建版本并发布。

#### 2.4 配置事件订阅

在「事件订阅」中配置：

1. **请求地址配置**：
   - 请求地址 URL：`https://your-domain/webhook`（本地开发时使用 ngrok 地址，见下文）
   - 加密策略：选择「不加密」（或根据需要选择加密）

2. **订阅事件**：
   - 搜索并添加事件：`im.message.receive_v1`（接收消息）

3. 点击「保存」

### 3. 本地开发环境设置（使用 ngrok）

由于飞书需要一个公网可访问的 URL 来发送回调，本地开发时需要使用内网穿透工具。

#### 3.1 安装 ngrok

1. 访问 [ngrok 官网](https://ngrok.com/) 注册账号
2. 下载并安装 ngrok
3. 使用您的 authtoken 进行认证：
   ```bash
   ngrok authtoken YOUR_AUTHTOKEN
   ```

#### 3.2 启动 ngrok

在新的终端窗口中运行：

```bash
ngrok http 5000
```

ngrok 会生成一个公网 URL，类似于：`https://abc123.ngrok.io`

#### 3.3 配置飞书事件订阅 URL

将 ngrok 生成的 URL + `/webhook` 填入飞书开放平台的事件订阅配置中：

```
https://abc123.ngrok.io/webhook
```

保存后，飞书会发送一个 challenge 请求验证 URL 是否可用。

### 4. 将机器人添加到飞书群

1. 在飞书中创建一个测试群组
2. 在群设置中，点击「添加机器人」
3. 搜索并添加您创建的机器人

## 使用方法

### 1. 启动服务

在项目目录下运行：

```bash
python AIcase.py
```

您应该看到类似的输出：

```
============================================================
飞书机器人 + Coze 工作流集成服务启动中...
监听地址: 0.0.0.0:5000
Webhook 路径: http://0.0.0.0:5000/webhook
============================================================
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

### 2. 在飞书群中使用

在添加了机器人的飞书群中，发送以下格式的消息：

```
@机器人名称 https://xxx.feishu.cn/docx/xxxxx
```

或者：

```
@机器人名称 请处理这个文档 https://xxx.feishu.cn/wiki/xxxxx
```

机器人会：
1. 自动提取文档链接
2. 触发 Coze 工作流处理
3. 在工作流完成后，发送一个富文本消息卡片通知结果

### 3. 查看日志

程序运行时会在控制台输出详细的日志信息，包括：
- 接收到的飞书回调事件
- 提取的文档链接
- Coze 工作流的执行状态
- 消息发送结果

## 配置说明

### config.py 配置项

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `COZE_API_TOKEN` | Coze API Token | 已填写 |
| `COZE_WORKFLOW_ID` | Coze 工作流 ID | 已填写 |
| `COZE_API_BASE` | Coze API 地址 | `https://api.coze.cn` |
| `FEISHU_APP_ID` | 飞书应用 ID | 需要填写 |
| `FEISHU_APP_SECRET` | 飞书应用 Secret | 需要填写 |
| `FEISHU_VERIFICATION_TOKEN` | 飞书验证 Token | 需要填写 |
| `FLASK_HOST` | Flask 监听地址 | `0.0.0.0` |
| `FLASK_PORT` | Flask 监听端口 | `5000` |
| `FLASK_DEBUG` | 是否开启调试模式 | `True` |

### 修改 Coze 工作流参数

如果您的 Coze 工作流需要不同的参数，可以在 `AIcase.py` 的 `handle_workflow_stream` 函数中修改：

```python
stream = coze_client.workflows.runs.stream(
    workflow_id=workflow_id,
    parameters={
        "doc_url": doc_url,
        # 添加其他参数
        "param1": "value1",
        "param2": "value2"
    }
)
```

## 故障排查

### 1. 飞书事件订阅配置失败

**问题**：配置请求地址时提示「请求失败」或「验证失败」

**解决方案**：
- 确认 ngrok 正在运行且 URL 正确
- 确认服务已启动（`python AIcase.py`）
- 检查防火墙是否阻止了连接
- 查看服务日志，确认是否收到了 challenge 请求

### 2. 机器人不响应消息

**问题**：在群中 @机器人发送消息，但没有任何反应

**解决方案**：
- 检查是否正确 @了机器人
- 确认消息中包含有效的飞书文档链接
- 查看服务日志，确认是否收到了消息事件
- 检查 `FEISHU_VERIFICATION_TOKEN` 是否配置正确

### 3. Coze 工作流调用失败

**问题**：服务日志显示工作流调用出错

**解决方案**：
- 确认 `COZE_API_TOKEN` 是否正确且未过期
- 确认 `COZE_WORKFLOW_ID` 是否正确
- 检查 Coze 工作流是否已发布
- 检查网络连接是否正常

### 4. 消息发送失败

**问题**：工作流执行成功，但飞书群中没有收到消息

**解决方案**：
- 检查机器人权限是否包含 `im:message:send_as_bot`
- 确认应用已发布（在「版本管理与发布」中）
- 查看日志中的错误信息
- 检查 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确

## API 接口

### 1. Webhook 接口

- **URL**: `/webhook`
- **方法**: `POST`
- **说明**: 接收飞书事件回调
- **请求体**: 飞书事件 JSON 数据

### 2. 健康检查接口

- **URL**: `/health`
- **方法**: `GET`
- **说明**: 检查服务是否正常运行
- **响应示例**:
  ```json
  {
    "status": "ok",
    "service": "飞书机器人 + Coze 工作流",
    "version": "1.0.0"
  }
  ```

### 3. 首页

- **URL**: `/`
- **方法**: `GET`
- **说明**: 显示服务信息

## 生产环境部署

如果要部署到生产环境（云服务器），建议：

1. **使用专业的 WSGI 服务器**：
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 AIcase:app
   ```

2. **使用进程管理工具**（如 supervisor 或 systemd）

3. **配置反向代理**（如 Nginx）

4. **使用 HTTPS**（申请 SSL 证书）

5. **设置环境变量**（不要在代码中硬编码敏感信息）

6. **关闭调试模式**：
   ```python
   FLASK_DEBUG = False
   ```

## 技术栈

- **Flask**: Web 框架，接收飞书回调
- **cozepy**: Coze Python SDK，调用工作流
- **requests**: HTTP 客户端，调用飞书 API
- **threading**: 后台任务处理

## 许可证

本项目仅供学习和参考使用。

## 联系方式

如有问题，请联系开发者或查看飞书开放平台文档：
- [飞书开放平台文档](https://open.feishu.cn/document/home/index)
- [Coze 开放平台文档](https://www.coze.cn/docs)


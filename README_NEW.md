# 🎯 Coze 工作流助手

一个简单美观的网页应用，将飞书文档链接提交给 Coze 工作流处理，完成后自动在飞书群内发送通知。

[![GitHub Pages](https://img.shields.io/badge/demo-live-success)](https://YOUR_USERNAME.github.io/coze-workflow-assistant/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ✨ 功能特点

- 🎨 **简洁美观的界面** - 现代化设计，响应式布局
- 🚀 **一键提交** - 输入飞书文档链接，自动触发 Coze 工作流
- 📱 **飞书通知** - 工作流完成后，通过自定义机器人发送群消息
- 🌐 **完全免费部署** - 前端部署到 GitHub Pages，后端部署到 Vercel/Render
- ⚡ **无需复杂配置** - 不需要企业应用，只需自定义机器人 Webhook

---

## 📸 预览

![界面预览](https://via.placeholder.com/800x500/667eea/ffffff?text=Coze+Workflow+Assistant)

*简洁美观的用户界面，轻松提交文档链接*

---

## 🚀 快速开始

### 方式一：使用在线部署版本（推荐）

如果您已经部署到 GitHub Pages：

1. 访问：`https://YOUR_USERNAME.github.io/coze-workflow-assistant/`
2. 输入飞书文档链接
3. 点击「开始处理」
4. 在飞书群查看处理结果

### 方式二：本地运行

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/coze-workflow-assistant.git
cd coze-workflow-assistant

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动后端
python api.py

# 4. 打开前端
# 用浏览器打开 frontend/index.html
```

---

## 📦 项目结构

```
coze-workflow-assistant/
├── frontend/              # 前端页面
│   ├── index.html        # 主页面
│   ├── style.css         # 样式文件
│   └── script.js         # 交互逻辑
├── api.py                # 后端 API
├── config.py             # 配置文件
├── utils.py              # 工具函数
├── requirements.txt      # Python 依赖
├── DEPLOY.md            # 部署指南
└── README.md            # 项目说明
```

---

## 🔧 配置说明

### 1. 获取 Coze 配置

- 访问 [Coze 平台](https://www.coze.cn)
- 获取 **API Token** 和 **Workflow ID**
- 填入 `config.py`

### 2. 配置飞书机器人

- 在飞书群中创建自定义机器人
- 获取 **Webhook URL**
- 填入 `config.py`

### 3. 部署

详细部署步骤请查看 **[DEPLOY.md](DEPLOY.md)**

---

## 📚 技术栈

### 前端
- HTML5 + CSS3
- 原生 JavaScript
- 响应式设计

### 后端
- Python 3.11
- Flask（Web 框架）
- Cozepy（Coze SDK）
- Requests（HTTP 客户端）

### 部署
- GitHub Pages（前端）
- Vercel / Render（后端）

---

## 🎯 使用场景

- 📄 **文档处理** - 提交文档链接，自动进行内容分析、总结等
- 🤖 **工作流自动化** - 触发 Coze 工作流进行各种自动化任务
- 📊 **数据处理** - 处理表格数据，生成报告
- 💬 **团队协作** - 处理完成后自动通知团队成员

---

## 📖 API 文档

### POST `/api/process`

提交文档进行处理

**请求体：**
```json
{
  "doc_url": "https://xxx.feishu.cn/docx/xxxxx"
}
```

**响应：**
```json
{
  "success": true,
  "message": "工作流已触发，处理完成后将在飞书群内收到通知",
  "result": "工作流执行结果"
}
```

### GET `/api/health`

健康检查

**响应：**
```json
{
  "status": "ok",
  "service": "Coze 工作流助手 API",
  "version": "2.0.0"
}
```

---

## 🔒 安全说明

- ✅ 敏感信息（Token、Secret）通过环境变量配置
- ✅ 前端验证文档链接格式
- ✅ 后端启用 CORS 保护
- ⚠️ 建议在生产环境关闭 Debug 模式

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🙏 致谢

- [Coze](https://www.coze.cn) - 强大的 AI 工作流平台
- [飞书](https://www.feishu.cn) - 高效的企业协作工具
- [Vercel](https://vercel.com) - 优秀的部署平台

---

## 📞 联系方式

- 项目主页：https://github.com/YOUR_USERNAME/coze-workflow-assistant
- 问题反馈：https://github.com/YOUR_USERNAME/coze-workflow-assistant/issues

---

**⭐ 如果这个项目对您有帮助，请给它一个 Star！**


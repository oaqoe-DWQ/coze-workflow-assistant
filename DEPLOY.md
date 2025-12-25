# 🚀 部署指南

本指南将帮助您将**前端页面**部署到 GitHub Pages，**后端 API** 部署到免费云平台（Vercel/Render）。

---

## 📦 项目结构

```
F:\AIcase\
├── frontend/               # 前端文件（部署到 GitHub Pages）
│   ├── index.html
│   ├── style.css
│   └── script.js
├── api.py                  # 后端 API（部署到 Vercel/Render）
├── config.py               # 配置文件
├── utils.py                # 工具函数
├── requirements.txt        # Python 依赖
├── vercel.json            # Vercel 配置
├── Procfile               # Heroku/Render 配置
└── runtime.txt            # Python 版本
```

---

## 第一步：准备 GitHub 仓库

### 1.1 创建 GitHub 仓库

1. 访问 [GitHub](https://github.com)
2. 点击右上角 **「+」** → **「New repository」**
3. 填写仓库信息：
   - Repository name: `coze-workflow-assistant`
   - Description: `飞书文档 + Coze 工作流集成`
   - 选择 **Public**（GitHub Pages 免费版需要公开仓库）
4. 点击 **「Create repository」**

### 1.2 上传代码到 GitHub

在项目目录下执行：

```bash
cd F:\AIcase

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: Coze 工作流助手"

# 关联远程仓库（替换为您的用户名和仓库名）
git remote add origin https://github.com/YOUR_USERNAME/coze-workflow-assistant.git

# 推送到 GitHub
git push -u origin main
```

如果遇到分支名称问题，执行：
```bash
git branch -M main
git push -u origin main
```

---

## 第二步：部署前端到 GitHub Pages

### 2.1 启用 GitHub Pages

1. 打开您的 GitHub 仓库
2. 点击 **「Settings」**（设置）
3. 在左侧菜单找到 **「Pages」**
4. 在 **Source** 部分：
   - Branch: 选择 `main`
   - Folder: 选择 `/frontend`
5. 点击 **「Save」**

### 2.2 等待部署完成

几分钟后，您会看到：
```
✅ Your site is live at https://YOUR_USERNAME.github.io/coze-workflow-assistant/
```

这就是您的前端页面地址！📱

---

## 第三步：部署后端 API

后端需要部署到支持 Python 的云平台。推荐以下免费平台：

### 选项 A：部署到 Vercel（推荐）⭐

#### A.1 注册 Vercel

1. 访问 [Vercel](https://vercel.com)
2. 使用 GitHub 账号登录

#### A.2 导入项目

1. 点击 **「Add New」** → **「Project」**
2. 选择 **「Import Git Repository」**
3. 找到并选择您的 `coze-workflow-assistant` 仓库
4. 点击 **「Import」**

#### A.3 配置项目

在配置页面：
- **Framework Preset**: 选择 **「Other」**
- **Root Directory**: 保持默认（`.`）
- **Build Command**: 留空
- **Output Directory**: 留空

#### A.4 添加环境变量

点击 **「Environment Variables」**，添加以下变量：

| Name | Value |
|------|-------|
| `COZE_API_TOKEN` | `cztei_hKynCJNCyYLWnkVC2uyJyiBFkUTblXe7T3XCghj66lwOUeKcVesnmzh2IQsP4FiKG` |
| `COZE_WORKFLOW_ID` | `7561294254754365486` |
| `FEISHU_CUSTOM_BOT_WEBHOOK` | `https://open.feishu.cn/open-apis/bot/v2/hook/61e7e70d-4cfb-4fc5-b51a-8a0b33317f46` |

#### A.5 部署

点击 **「Deploy」**，等待几分钟。

部署成功后，您会得到后端 API 地址：
```
https://your-project.vercel.app
```

---

### 选项 B：部署到 Render

#### B.1 注册 Render

1. 访问 [Render](https://render.com)
2. 使用 GitHub 账号登录

#### B.2 创建 Web Service

1. 点击 **「New」** → **「Web Service」**
2. 连接您的 GitHub 仓库
3. 填写配置：
   - **Name**: `coze-workflow-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api:app`

#### B.3 添加环境变量

在 **Environment** 部分添加：
- `COZE_API_TOKEN`
- `COZE_WORKFLOW_ID`
- `FEISHU_CUSTOM_BOT_WEBHOOK`

#### B.4 部署

点击 **「Create Web Service」**。

部署成功后，您会得到 API 地址：
```
https://your-service.onrender.com
```

---

## 第四步：连接前端和后端

### 4.1 修改前端配置

编辑 `frontend/script.js` 文件，修改 API 地址：

```javascript
const API_CONFIG = {
    // 替换为您的后端 API 地址
    baseUrl: 'https://your-project.vercel.app'  // 或 Render 的地址
};
```

### 4.2 重新部署前端

```bash
git add frontend/script.js
git commit -m "Update API endpoint"
git push origin main
```

GitHub Pages 会自动重新部署（几分钟后生效）。

---

## 第五步：测试

### 5.1 访问前端页面

打开您的 GitHub Pages 地址：
```
https://YOUR_USERNAME.github.io/coze-workflow-assistant/
```

### 5.2 测试功能

1. 输入飞书文档链接
2. 点击「开始处理」
3. 查看飞书群是否收到通知

---

## ✅ 完整的访问地址

部署完成后，您将拥有：

| 服务 | 地址 | 说明 |
|------|------|------|
| 🌐 前端页面 | `https://YOUR_USERNAME.github.io/coze-workflow-assistant/` | 用户访问的网页 |
| 🔧 后端 API | `https://your-project.vercel.app` | API 服务 |
| 💬 飞书群通知 | 自动发送 | 工作流完成后通知 |

---

## 🔧 常见问题

### Q1: GitHub Pages 显示 404

**原因**：文件路径配置错误

**解决**：
1. 检查 Settings → Pages 中的 Folder 是否选择了 `/frontend`
2. 确保 `frontend` 文件夹中有 `index.html`

### Q2: 前端无法连接后端

**原因**：CORS 跨域问题或 API 地址错误

**解决**：
1. 确认 `script.js` 中的 `baseUrl` 地址正确
2. 检查后端是否已启用 CORS（已在 `api.py` 中配置）
3. 查看浏览器控制台的错误信息

### Q3: Vercel 部署失败

**原因**：配置文件或依赖问题

**解决**：
1. 检查 `vercel.json` 文件是否正确
2. 确认 `requirements.txt` 中的依赖版本
3. 查看 Vercel 部署日志中的错误信息

### Q4: 后端 API 调用 Coze 失败

**原因**：环境变量未配置或 Token 无效

**解决**：
1. 在 Vercel/Render 中检查环境变量是否正确设置
2. 确认 Coze Token 是否有效
3. 查看后端日志

### Q5: 飞书群收不到消息

**原因**：Webhook URL 错误或机器人未添加到群

**解决**：
1. 确认 `FEISHU_CUSTOM_BOT_WEBHOOK` 地址正确
2. 检查自定义机器人是否已添加到目标群组
3. 测试 Webhook 是否可用

---

## 📱 本地测试

在部署前，可以在本地测试：

### 启动后端

```bash
cd F:\AIcase
pip install -r requirements.txt
python api.py
```

后端将运行在 `http://localhost:5000`

### 测试前端

1. 用浏览器打开 `frontend/index.html`
2. 或使用 Live Server 插件（VS Code）

确保 `script.js` 中的 `baseUrl` 设置为 `http://localhost:5000`

---

## 🎉 完成！

恭喜！您已经成功部署了完整的系统：

✅ 用户访问前端页面  
✅ 输入飞书文档链接  
✅ 后端调用 Coze 工作流  
✅ 飞书群收到处理完成通知  

享受您的自动化工作流吧！🚀

---

## 📞 需要帮助？

- GitHub Pages 文档：https://docs.github.com/pages
- Vercel 文档：https://vercel.com/docs
- Render 文档：https://render.com/docs
- Coze 文档：https://www.coze.cn/docs


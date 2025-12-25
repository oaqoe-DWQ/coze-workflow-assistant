# ⚡ 5分钟快速部署指南

按照以下步骤，5分钟内完成部署！

---

## 📋 准备清单

- [ ] GitHub 账号
- [ ] 飞书自定义机器人 Webhook（您已有）
- [ ] Coze API Token 和 Workflow ID（您已有）

---

## 🚀 三步部署

### 第 1 步：上传到 GitHub（2分钟）

```bash
# 在项目目录执行
cd F:\AIcase

git init
git add .
git commit -m "Initial commit"

# 替换为您的 GitHub 用户名
git remote add origin https://github.com/YOUR_USERNAME/coze-workflow-assistant.git
git branch -M main
git push -u origin main
```

**如果还没创建仓库：**
1. 访问 https://github.com/new
2. 仓库名：`coze-workflow-assistant`
3. 类型：Public
4. 点击 Create

---

### 第 2 步：部署前端到 GitHub Pages（1分钟）

1. 打开您的仓库页面
2. **Settings** → **Pages**
3. **Source** 选择：
   - Branch: `main`
   - Folder: `/frontend`
4. 点击 **Save**

**等待 2-3 分钟**，您会得到前端地址：
```
https://YOUR_USERNAME.github.io/coze-workflow-assistant/
```

---

### 第 3 步：部署后端到 Vercel（2分钟）

1. 访问 https://vercel.com
2. 用 GitHub 登录
3. **New Project** → 选择 `coze-workflow-assistant` 仓库
4. **Import**
5. 在 **Environment Variables** 添加：

```
COZE_API_TOKEN = cztei_hKynCJNCyYLWnkVC2uyJyiBFkUTblXe7T3XCghj66lwOUeKcVesnmzh2IQsP4FiKG
COZE_WORKFLOW_ID = 7561294254754365486
FEISHU_CUSTOM_BOT_WEBHOOK = https://open.feishu.cn/open-apis/bot/v2/hook/61e7e70d-4cfb-4fc5-b51a-8a0b33317f46
```

6. 点击 **Deploy**

**等待 2-3 分钟**，您会得到后端地址：
```
https://your-project.vercel.app
```

---

## 🔗 连接前端和后端

### 修改前端配置

1. 编辑 `frontend/script.js`
2. 找到第 4 行：
```javascript
baseUrl: 'http://localhost:5000'
```
3. 改为您的 Vercel 地址：
```javascript
baseUrl: 'https://your-project.vercel.app'
```
4. 保存并推送：
```bash
git add frontend/script.js
git commit -m "Update API endpoint"
git push
```

---

## ✅ 完成！

🎉 恭喜！您的系统已经部署完成：

- **前端地址**：`https://YOUR_USERNAME.github.io/coze-workflow-assistant/`
- **后端地址**：`https://your-project.vercel.app`

---

## 🧪 测试

1. 打开前端页面
2. 输入任意飞书文档链接（如 `https://xxx.feishu.cn/docx/xxxxx`）
3. 点击「开始处理」
4. 查看飞书群是否收到通知

---

## ❓ 遇到问题？

### 问题 1：GitHub Pages 显示 404
- 等待 3-5 分钟，GitHub Pages 需要时间生效
- 检查 Settings → Pages 配置是否正确

### 问题 2：前端连接后端失败
- 确认 `script.js` 中的后端地址已更新
- 清除浏览器缓存
- 查看浏览器控制台错误信息（F12）

### 问题 3：Vercel 部署失败
- 检查 `vercel.json` 文件是否存在
- 确认环境变量已正确添加
- 查看 Vercel 部署日志

---

## 📚 更多帮助

- 详细部署指南：[DEPLOY.md](DEPLOY.md)
- 完整文档：[README_NEW.md](README_NEW.md)
- 问题反馈：GitHub Issues

---

**享受您的自动化工作流！** 🚀


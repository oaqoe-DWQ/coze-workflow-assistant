// API 配置
const API_CONFIG = {
    // 本地开发时使用
    // baseUrl: 'http://localhost:5000'
    
    // 部署后需要修改为您的后端 API 地址
    // 例如部署到 Vercel/Render 后的地址
    baseUrl: 'http://localhost:5000'  // 请在部署时修改此地址
};

// DOM 元素
const form = document.getElementById('documentForm');
const docUrlInput = document.getElementById('docUrl');
const submitBtn = document.getElementById('submitBtn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');
const statusMessage = document.getElementById('statusMessage');

// 表单提交处理
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const docUrl = docUrlInput.value.trim();
    
    // 验证链接格式
    if (!isValidFeishuUrl(docUrl)) {
        showMessage('error', '请输入有效的飞书文档链接！');
        return;
    }
    
    // 开始处理
    setLoading(true);
    hideMessage();
    
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}/api/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ doc_url: docUrl })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            showMessage('success', '✅ 工作流已触发！处理完成后将在飞书群内收到通知。');
            docUrlInput.value = ''; // 清空输入框
        } else {
            showMessage('error', `处理失败: ${data.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('请求失败:', error);
        
        if (error.message.includes('Failed to fetch')) {
            showMessage('error', '⚠️ 无法连接到后端服务，请确保后端服务正在运行。');
        } else {
            showMessage('error', `请求失败: ${error.message}`);
        }
    } finally {
        setLoading(false);
    }
});

// 验证飞书文档链接
function isValidFeishuUrl(url) {
    const pattern = /https:\/\/[a-zA-Z0-9\-]+\.(feishu|larkoffice)\.(cn|com)\/(docx|wiki|docs|sheets|base|file)\/[a-zA-Z0-9\-_]+/;
    return pattern.test(url);
}

// 设置加载状态
function setLoading(loading) {
    if (loading) {
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
    } else {
        submitBtn.disabled = false;
        btnText.style.display = 'block';
        btnLoader.style.display = 'none';
    }
}

// 显示状态消息
function showMessage(type, message) {
    statusMessage.className = `status-message ${type}`;
    statusMessage.textContent = message;
    statusMessage.style.display = 'flex';
    
    // 自动隐藏成功消息
    if (type === 'success') {
        setTimeout(() => {
            hideMessage();
        }, 5000);
    }
}

// 隐藏状态消息
function hideMessage() {
    statusMessage.style.display = 'none';
}

// 输入框实时验证
docUrlInput.addEventListener('input', (e) => {
    const url = e.target.value.trim();
    
    if (url && !isValidFeishuUrl(url)) {
        docUrlInput.style.borderColor = '#f56565';
    } else {
        docUrlInput.style.borderColor = '#e2e8f0';
    }
});

// 自动聚焦输入框
window.addEventListener('load', () => {
    docUrlInput.focus();
});


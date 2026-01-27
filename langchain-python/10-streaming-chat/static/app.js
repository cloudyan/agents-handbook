let ws = null;
let isStreaming = false;

function connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/chat`);

    ws.onopen = () => {
        updateStatus(true);
        appendMessage('已连接到服务器', 'system');
    };

    ws.onclose = () => {
        updateStatus(false);
        appendMessage('与服务器断开连接', 'system');
        isStreaming = false;
        const button = document.getElementById('send-button');
        if (button) {
            button.disabled = false;
            button.textContent = '发送';
        }
    };

    ws.onerror = (error) => {
        console.error('WebSocket 错误:', error);
        appendMessage('连接错误，请刷新页面重试', 'system');
    };

    ws.onmessage = (event) => {
        if (event.data === '[STREAM_END]') {
            isStreaming = false;
            const button = document.getElementById('send-button');
            if (button) {
                button.disabled = false;
                button.textContent = '发送';
            }

            const currentResponse = document.getElementById('current-response');
            if (currentResponse) {
                currentResponse.removeAttribute('id');
                currentResponse.innerHTML = currentResponse.textContent.replace(/\n/g, '<br>');
            }
        } else {
            handleStreamMessage(event.data);
        }
    };
}

function updateStatus(connected) {
    const indicator = document.getElementById('status');
    const text = document.getElementById('status-text');

    if (connected) {
        indicator.classList.remove('disconnected');
        indicator.classList.add('connected');
        text.textContent = '已连接';
    } else {
        indicator.classList.remove('connected');
        indicator.classList.add('disconnected');
        text.textContent = '未连接';
    }

    console.log('状态更新:', connected, indicator.className);
}

function appendMessage(content, type = 'assistant') {
    const messagesDiv = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;

    if (type === 'system') {
        if (content.includes('已连接')) {
            messageDiv.classList.add('system-success');
        } else {
            messageDiv.classList.add('system-error');
        }
    }

    if (type === 'assistant' && isStreaming) {
        messageDiv.id = 'current-response';
    }

    messageDiv.innerHTML = content.replace(/\\n/g, '<br>');
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;

    return messageDiv;
}

function handleStreamMessage(content) {
    let currentResponse = document.getElementById('current-response');

    if (!currentResponse) {
        currentResponse = appendMessage('', 'assistant');
    }

    currentResponse.textContent += content;
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}

function sendMessage() {
    const input = document.getElementById('message-input');
    const button = document.getElementById('send-button');
    const message = input.value.trim();

    if (!message || !ws || ws.readyState !== WebSocket.OPEN || isStreaming) {
        return;
    }

    appendMessage(message, 'user');
    input.value = '';

    isStreaming = true;
    button.disabled = true;
    button.innerHTML = '<span class="loading"></span>';

    ws.send(message);
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !isStreaming) {
        sendMessage();
    }
}

window.onload = connect;

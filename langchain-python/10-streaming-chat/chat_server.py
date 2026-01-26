#!/usr/bin/env python3
"""
10 - 流式输出 + ChatUI
FastAPI + WebSocket 实现实时聊天
"""

import os
import json
from typing import AsyncGenerator
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="LangChain Streaming Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatSession:
    """聊天会话管理"""

    def __init__(self, llm):
        self.llm = llm
        self.message_history = []

    async def stream_response(self, message: str) -> AsyncGenerator[str, None]:
        """流式生成响应"""
        self.message_history.append({"role": "user", "content": message})

        try:
            async for chunk in self.llm.astream(message):
                if chunk.content:
                    yield chunk.content

            self.message_history.append({"role": "assistant", "content": "完整响应"})
        except Exception as e:
            yield f"\n[错误: {str(e)}]"


chat_sessions = {}


def get_html_content() -> str:
    """生成聊天界面 HTML"""
    return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LangChain 流式聊天</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .chat-container {
            width: 90%;
            max-width: 800px;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }

        .chat-header h1 {
            font-size: 1.5rem;
            margin-bottom: 5px;
        }

        .chat-header p {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f5f5f5;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 12px;
            max-width: 80%;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }

        .message.assistant {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }

        .message.system {
            background: #ffebee;
            color: #c62828;
            text-align: center;
            max-width: 100%;
            font-size: 0.9rem;
        }

        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
            display: flex;
            gap: 10px;
        }

        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 1rem;
            outline: none;
            transition: border-color 0.3s;
        }

        .chat-input input:focus {
            border-color: #667eea;
        }

        .chat-input button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 1rem;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .chat-input button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .chat-input button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-indicator.connected {
            background: #4caf50;
        }

        .status-indicator.disconnected {
            background: #f44336;
        }

        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #f3f3f3;
            border-top: 2px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🦜🔗 LangChain 流式聊天</h1>
            <p>
                <span class="status-indicator disconnected" id="status"></span>
                <span id="status-text">未连接</span>
            </p>
        </div>

        <div class="chat-messages" id="messages"></div>

        <div class="chat-input">
            <input
                type="text"
                id="message-input"
                placeholder="输入消息..."
                onkeypress="handleKeyPress(event)"
            />
            <button id="send-button" onclick="sendMessage()">发送</button>
        </div>
    </div>

    <script>
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
            };

            ws.onerror = (error) => {
                console.error('WebSocket 错误:', error);
                appendMessage('连接错误，请刷新页面重试', 'system');
            };

            ws.onmessage = (event) => {
                handleStreamMessage(event.data);
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
        }

        function appendMessage(content, type = 'assistant') {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}`;

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

            currentResponse.innerHTML += content.replace(/\\n/g, '<br>');
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }

        function sendMessage() {
            const input = document.getElementById('message-input');
            const button = document.getElementById('send-button');
            const message = input.value.trim();

            if (!message || !ws || ws.readyState !== WebSocket.OPEN) {
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
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        ws.onclose = () => {
            isStreaming = false;
            const button = document.getElementById('send-button');
            if (button) {
                button.disabled = false;
                button.textContent = '发送';
            }
        };

        window.onload = connect;
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def get_chat_interface():
    """获取聊天界面"""
    return get_html_content()


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 聊天端点"""
    await websocket.accept()
    client_id = id(websocket)

    try:
        # 从环境变量读取配置
        openai_api_key = os.getenv("OPENAI_API_KEY", "")
        openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

        if not openai_api_key:
            await websocket.send_text("❌ 请设置 OPENAI_API_KEY 环境变量")
            await websocket.close()
            return

        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )
        session = ChatSession(llm)
        chat_sessions[client_id] = session

        print(f"✓ 客户端 {client_id} 已连接")

        while True:
            data = await websocket.receive_text()
            print(f"收到消息: {data[:50]}...")

            try:
                async for chunk in session.stream_response(data):
                    await websocket.send_text(chunk)

            except Exception as e:
                error_msg = f"\\n[错误: {str(e)}]"
                await websocket.send_text(error_msg)
                print(f"处理错误: {e}")

    except WebSocketDisconnect:
        print(f"✗ 客户端 {client_id} 断开连接")
    except Exception as e:
        print(f"WebSocket 错误: {e}")
    finally:
        if client_id in chat_sessions:
            del chat_sessions[client_id]


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "active_sessions": len(chat_sessions)}


def main():
    import uvicorn

    print("🦜🔗 09 - 流式输出 + ChatUI")
    print("=" * 60)
    print("启动服务器...")
    print("访问: http://localhost:8000")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

import dotenv from "dotenv";
import express from "express";
import { WebSocketServer, WebSocket } from "ws";
import { createServer } from "http";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "@langchain/core/messages";

dotenv.config({ override: true });

const app = express();
const server = createServer(app);

const PORT = process.env.PORT || 8000;

app.use(express.json());

const apiKey = process.env.OPENAI_API_KEY;
const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

if (!apiKey) {
  console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
  process.exit(1);
}

app.get("/", (_req, res) => {
  res.setHeader("Content-Type", "text/html");
  res.send(getHtmlContent());
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

const wss = new WebSocketServer({ server });

interface ChatSession {
  llm: ChatOpenAI;
  messageHistory: { role: string; content: string }[];
}

const chatSessions = new Map<WebSocket, ChatSession>();

async function* streamResponse(
  llm: ChatOpenAI,
  message: string,
  session: ChatSession
): AsyncGenerator<string, void, unknown> {
  session.messageHistory.push({ role: "user", content: message });

  try {
    const stream = await llm.stream([new HumanMessage(message)]);

    for await (const chunk of stream) {
      if (chunk.content) {
        yield chunk.content as string;
      }
    }

    session.messageHistory.push({ role: "assistant", content: "完整响应" });
  } catch (e) {
    yield `\n[错误: ${e instanceof Error ? e.message : String(e)}]`;
  }
}

wss.on("connection", (ws: WebSocket) => {
  const clientId = ws;

  try {
    const llm = new ChatOpenAI({
      modelName,
      openAIApiKey: apiKey,
      configuration: { baseURL },
      temperature: 0.7,
    });

    const session: ChatSession = {
      llm,
      messageHistory: [],
    };

    chatSessions.set(ws, session);

    console.log(`✓ 客户端已连接`);

    ws.on("message", async (data: Buffer) => {
      const message = data.toString();
      console.log(`收到消息: ${message.slice(0, 50)}...`);

      try {
        for await (const chunk of streamResponse(llm, message, session)) {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(chunk);
          }
        }
      } catch (e) {
        const errorMsg = `\n[错误: ${e instanceof Error ? e.message : String(e)}]`;
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(errorMsg);
        }
        console.log(`处理错误: ${e}`);
      }
    });

    ws.on("close", () => {
      console.log(`✗ 客户端断开连接`);
      chatSessions.delete(ws);
    });

    ws.on("error", (error) => {
      console.log(`WebSocket 错误: ${error}`);
    });
  } catch (e) {
    console.log(`初始化错误: ${e}`);
    ws.close();
  }
});

function getHtmlContent(): string {
  return `<!DOCTYPE html>
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
            ws = new WebSocket(\`\${protocol}//\${window.location.host}\`);

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
            messageDiv.className = \`message \${type}\`;

            if (type === 'assistant' && isStreaming) {
                messageDiv.id = 'current-response';
            }

            messageDiv.innerHTML = content.replace(/\\\\n/g, '<br>');
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            return messageDiv;
        }

        function handleStreamMessage(content) {
            let currentResponse = document.getElementById('current-response');

            if (!currentResponse) {
                currentResponse = appendMessage('', 'assistant');
            }

            currentResponse.innerHTML += content.replace(/\\\\n/g, '<br>');
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
</html>`;
}

server.listen(PORT, () => {
  console.log("🦜🔗 10 - 流式输出 + ChatUI");
  console.log("=".repeat(60));
  console.log(`启动服务器...`);
  console.log(`访问: http://localhost:${PORT}`);
  console.log("=".repeat(60));
});

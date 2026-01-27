# 10 - 流式输出 + ChatUI

展示如何实现流式输出和简单的聊天界面，提供实时交互体验。已对齐 TypeScript 版本实现。

## 核心特性

### 1. 流式输出
```python
# 传统方式：等待完整响应
response = llm.invoke("问题")
print(response.content)

# 流式方式：实时输出
async for chunk in llm.astream("问题"):
    print(chunk.content, end="", flush=True)
```

**优势：**
- 降低感知延迟
- 提升用户体验
- 支持超长文本输出
- 可以提前终止

### 2. WebSocket 实时通信
```
浏览器 → WebSocket → FastAPI → LangChain → 流式输出 → WebSocket → 浏览器
```

### 3. 多轮对话记忆
```python
# 自动维护对话历史
session.state.add_user_message("你好")
session.state.add_assistant_message("你好！有什么可以帮助你的？")

# LLM 会基于完整历史进行响应
messages = session.state.get_messages_for_llm("再见")
```

### 4. 流结束标志
```python
# 后端发送结束标志
await websocket.send_text("[STREAM_END]")

# 前端识别并处理
if (event.data === '[STREAM_END]') {
    isStreaming = false;
    // 恢复按钮状态
}
```

## 运行方法

### 后端服务
```bash
cd langchain-python
python 10-streaming-chat/chat_server.py
```

### 前端界面
打开浏览器访问：`http://localhost:8000`

## 项目结构

```
10-streaming-chat/
├── chat_server.py      # FastAPI + WebSocket 服务器（主文件）
├── models.py           # Pydantic 数据模型
├── static/             # 前端静态文件
│   ├── index.html      # 聊天界面 HTML
│   ├── styles.css      # 样式文件
│   └── app.js          # 前端逻辑 JavaScript
└── README.md           # 说明文档
```

## 技术栈

- **后端**: FastAPI + WebSocket
- **前端**: 原生 HTML/JavaScript/CSS
- **流式**: LangChain Streaming API
- **实时通信**: WebSocket 协议
- **类型安全**: Pydantic 数据模型

## 核心代码

### WebSocket 端点
```python
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        async for chunk in session.stream_response(data):
            await websocket.send_text(chunk)
        await websocket.send_text("[STREAM_END]")  # 流结束标志
```

### 多轮对话管理
```python
class ChatSessionState(BaseModel):
    message_history: List[Message] = Field(default_factory=list)

    def add_user_message(self, content: str) -> None:
        self.message_history.append(Message(role="user", content=content))

    def get_messages_for_llm(self, current_message: str) -> List[dict]:
        messages = [{"role": msg.role, "content": msg.content}
                    for msg in self.message_history]
        messages.append({"role": "user", "content": current_message})
        return messages
```

### 前端 WebSocket 连接
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/chat");

ws.onmessage = (event) => {
    if (event.data === '[STREAM_END]') {
        isStreaming = false;
        // 恢复按钮状态
    } else {
        handleStreamMessage(event.data);
    }
};
```

## 与 TypeScript 版本对齐

| 特性 | Python | TypeScript | 对齐状态 |
|------|--------|------------|----------|
| 文件分离 | ✅ static/ 目录 | ✅ 独立文件 | ✅ 已对齐 |
| 流结束标志 | ✅ [STREAM_END] | ✅ [STREAM_END] | ✅ 已对齐 |
| 多轮对话 | ✅ ChatSessionState | ✅ ChatSession | ✅ 已对齐 |
| 类型安全 | ✅ Pydantic | ✅ TypeScript | ✅ 已对齐 |
| 前端状态管理 | ✅ isStreaming | ✅ isStreaming | ✅ 已对齐 |

## 使用场景

1. **实时对话系统**
2. **代码生成助手**
3. **文档问答系统**
4. **AI 客服机器人**

## 扩展功能

- [ ] 用户认证
- [ ] 流量限制
- [ ] 消息持久化存储
- [ ] 多用户支持
- [ ] 错误重连机制
- [ ] 打字机效果优化

## 下一步

完成流式输出学习后，可以继续探索：
- 11-生产级追踪（LangSmith）
- 12-Agent Chat 基础版
- 13-Agent Chat 完整版

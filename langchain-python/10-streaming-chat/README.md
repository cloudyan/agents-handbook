# 10 - 流式输出 + ChatUI

展示如何实现流式输出和简单的聊天界面，提供实时交互体验。

## 核心特性

### 1. 流式输出
```python
# 传统方式：等待完整响应
response = llm.invoke("问题")
print(response.content)

# 流式方式：实时输出
for chunk in llm.stream("问题"):
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

## 运行方法

### 后端服务
```bash
cd langchain-python/10-streaming-chat
python chat_server.py
```

### 前端界面
打开浏览器访问：`http://localhost:8000`

## 项目结构

```
10-streaming-chat/
├── chat_server.py      # FastAPI + WebSocket 服务器
├── static/
│   └── index.html      # 聊天界面
├── templates/
│   └── chat.html       # 聊天模板
└── requirements.txt    # 额外依赖
```

## 技术栈

- **后端**: FastAPI + WebSocket
- **前端**: 原生 HTML/JavaScript
- **流式**: LangChain Streaming API
- **实时通信**: WebSocket协议

## 核心代码

### WebSocket 端点
```python
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        async for chunk in llm.astream(data):
            await websocket.send_text(chunk.content)
```

### 前端 WebSocket 连接
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/chat");
ws.onmessage = (event) => {
    appendMessage(event.data, "assistant");
};
```

## 使用场景

1. **实时对话系统**
2. **代码生成助手**
3. **文档问答系统**
4. **AI 客服机器人**

## 扩展功能

- [ ] 多轮对话记忆
- [ ] 打字机效果
- [ ] 消息历史记录
- [ ] 用户认证
- [ ] 流量限制
- [ ] 错误重连

## 下一步

完成流式输出学习后，可以继续探索：
- 11-生产级追踪（LangSmith）
- 多模态输入（图片、语音）
- 高级 RAG 优化

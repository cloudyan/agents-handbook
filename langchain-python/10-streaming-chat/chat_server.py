#!/usr/bin/env python3
"""
10 - 流式输出 + ChatUI
FastAPI + WebSocket 实现实时聊天，参考 TypeScript 版本实现
"""

import os
import sys
from typing import AsyncGenerator
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

load_dotenv(override=True)


# sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import ChatSessionState, HealthResponse # type: ignore


app = FastAPI(title="LangChain Streaming Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ChatSession:
    """聊天会话管理"""

    def __init__(self, llm):
        self.llm = llm
        self.state = ChatSessionState()

    async def stream_response(self, message: str) -> AsyncGenerator[str, None]:
        """流式生成响应，支持多轮对话"""
        self.state.add_user_message(message)

        try:
            messages = self.state.get_messages_for_llm(message)

            full_response = ""
            async for chunk in self.llm.astream(messages):
                if chunk.content:
                    content = chunk.content
                    full_response += content
                    yield content

            self.state.add_assistant_message(full_response)

        except Exception as e:
            error_msg = f"\n[错误: {str(e)}]"
            self.state.add_assistant_message(error_msg)
            yield error_msg


chat_sessions: dict[int, ChatSession] = {}


@app.get("/")
async def get_chat_interface():
    """获取聊天界面"""
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html"))


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket 聊天端点"""
    await websocket.accept()
    client_id = id(websocket)

    try:
        if not os.getenv("OPENAI_API_KEY"):
            await websocket.send_text("❌ 请设置 OPENAI_API_KEY 环境变量")
            await websocket.close()
            return

        from clients import create_model_client

        llm = create_model_client(temperature=0.7)
        session = ChatSession(llm)
        chat_sessions[client_id] = session

        print(f"✓ 客户端 {client_id} 已连接")

        while True:
            data = await websocket.receive_text()
            print(f"收到消息: {data[:50]}...")

            try:
                print("开始处理响应...")
                chunk_count = 0
                async for chunk in session.stream_response(data):
                    if websocket.client_state.name == "CONNECTED":
                        await websocket.send_text(chunk)
                        chunk_count += 1
                        if chunk_count % 10 == 0:
                            print(f"已发送 {chunk_count} 个 chunk")
                    else:
                        print("连接已断开，停止发送")
                        break

                print(f"流式输出完成，共发送 {chunk_count} 个 chunk")
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_text("[STREAM_END]")

            except Exception as e:
                import traceback
                print(f"处理错误: {e}")
                traceback.print_exc()
                error_msg = f"\n[错误: {str(e)}]"
                if websocket.client_state.name == "CONNECTED":
                    await websocket.send_text(error_msg)
                    await websocket.send_text("[STREAM_END]")

    except WebSocketDisconnect:
        print(f"✗ 客户端 {client_id} 断开连接")
    except Exception as e:
        print(f"WebSocket 错误: {e}")
    finally:
        if client_id in chat_sessions:
            del chat_sessions[client_id]


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="ok",
        active_sessions=len(chat_sessions),
        timestamp=datetime.now().isoformat()
    )


def main():
    import uvicorn

    print("🦜🔗 10 - 流式输出 + ChatUI")
    print("=" * 60)
    print("启动服务器...")
    print("访问: http://localhost:8000")
    print("=" * 60)

    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()

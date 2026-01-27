#!/usr/bin/env python3
"""
06 - API Deployment
使用 FastAPI 部署天气智能体为 HTTP 服务，参考 TypeScript 版本实现
"""

import os
import sys
import json
import httpx
import uvicorn
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv(override=True)

if not os.getenv("OPENAI_API_KEY"):
    print("警告：请设置 OPENAI_API_KEY 环境变量")

if not os.getenv("OPENWEATHER_API_KEY"):
    print("警告：请设置 OPENWEATHER_API_KEY 环境变量")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PORT = int(os.getenv("PORT", "8000"))

app = FastAPI(
    title="LangChain 天气智能体 API",
    description="基于 LangChain 的天气查询和智能建议 API",
    version="1.0.0",
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class HealthResponse(BaseModel):
    status: str
    langchain_available: bool
    openai_configured: bool
    openweather_configured: bool


try:
    from langchain.agents import create_agent
    from langchain.tools import tool
    from langchain_core.messages import HumanMessage
    from clients import create_model_client

    LANGCHAIN_AVAILABLE = True

    @tool
    def get_weather(location: str, days: int = 1) -> str:
        """获取指定城市的天气预报，包括温度、天气状况和降雨概率。

        Args:
            location (str): 城市英文名称，例如 Beijing, Shanghai
            days (int): 预报天数，默认为1天

        Returns:
            str: 天气预报信息
        """
        try:
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key:
                return "OPENWEATHER_API_KEY 环境变量未设置"

            url = f"https://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric",
                "cnt": days * 8,
            }

            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()

            forecasts = data["list"][: days * 8]
            result = f"{location} 天气预报：\n"

            for item in forecasts:
                from datetime import datetime
                date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                condition = item["weather"][0]["description"]
                temp = item["main"]["temp"]
                result += f"{date} {condition}, 温度: {temp}°C\n"

            return result
        except Exception as e:
            return f"获取天气失败: {str(e)}"

    @tool
    def calculate(expression: str) -> str:
        """计算数学表达式。

        Args:
            expression (str): 数学表达式，如 "2 + 3 * 4"

        Returns:
            str: 计算结果
        """
        try:
            result = eval(expression)
            return f"计算结果：{result}"
        except:
            return "计算错误，请检查表达式"

    llm = create_model_client(temperature=0, streaming=True)
    system_prompt = "你是一个智能助手，可以使用工具来帮助用户回答问题。请根据用户的问题，决定是否需要调用工具，并给出最终答案。请用中文回答问题。"

    agent = create_agent(
        model=llm,
        tools=[get_weather, calculate],
        system_prompt=system_prompt,
    )

    print("✓ 智能体初始化完成")

except ImportError as e:
    print(f"❌ 导入错误：{e}")
    LANGCHAIN_AVAILABLE = False
    agent = None
except Exception as e:
    print(f"❌ 智能体初始化失败：{e}")
    LANGCHAIN_AVAILABLE = False
    agent = None


@app.get("/", response_model=Dict[str, Any])
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "LangChain 智能体 API Server (使用 createAgent)",
        "endpoints": {
            "/chat": "POST - 与 Agent 对话（支持工具调用）",
            "/chat/stream": "POST - 与 Agent 对话（SSE 流式输出）",
            "/health": "GET - 健康检查",
        },
        "tools": ["get_weather", "calculate"],
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="ok",
        langchain_available=LANGCHAIN_AVAILABLE,
        openai_configured=bool(os.getenv("OPENAI_API_KEY")),
        openweather_configured=bool(os.getenv("OPENWEATHER_API_KEY")),
    )


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """智能体对话 API"""
    global agent

    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")

    try:
        print(f"\n[{request.session_id or 'anonymous'}] 用户问题: {request.message}")
        print("-" * 50)

        response = await agent.ainvoke(
            {"messages": [HumanMessage(content=request.message)]}
        )

        answer = response["messages"][-1].content

        print(f"\n最终回答: {answer}")
        print("=" * 50)

        return {
            "message": answer,
            "timestamp": __import__("datetime").datetime.now().isoformat(),
        }
    except Exception as e:
        print(f"❌ 处理请求时出错: {e}")
        raise HTTPException(status_code=500, detail=f"处理请求失败: {str(e)}")


async def generate_streaming_response(message: str, session_id: str | None = None):
    """生成流式响应"""
    try:
        print(f"\n[{session_id or 'anonymous'}] 用户问题 (流式): {message}")
        print("-" * 50)

        async for token, metadata in agent.astream(
            {"messages": [{"role": "user", "content": message}]},
            stream_mode="messages",
        ):
            if hasattr(token, "content_blocks"):
                for block in token.content_blocks:
                    if block.get("type") == "text":
                        text = block.get("text", "")
                        if text:
                            yield f"data: {json.dumps({'content': text, 'type': 'message'}, ensure_ascii=False)}\n\n"
                            print(f"[流式输出] {text[:50]}...")

        yield f"data: {json.dumps({'type': 'done'}, ensure_ascii=False)}\n\n"
        print("\n流式输出完成")
        print("=" * 50)

    except Exception as e:
        print(f"❌ 处理流式请求时出错: {e}")
        yield f"data: {json.dumps({'error': str(e), 'type': 'error'}, ensure_ascii=False)}\n\n"


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """智能体对话 API（流式输出）"""
    global agent

    if not agent:
        raise HTTPException(status_code=500, detail="智能体未初始化")

    return StreamingResponse(
        generate_streaming_response(request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no",
        },
    )


if __name__ == "__main__":
    print("\n🚀 LangChain Agent API Server")
    print("=" * 50)
    print(f"服务器运行在 http://localhost:{PORT}")
    print(f"API 文档: http://localhost:{PORT}/")
    print("=" * 50)
    print("\n可用工具:")
    print("  - get_weather: 查询天气预报")
    print("  - calculate: 数学计算")

    print("\n示例请求:")
    print(f'curl -X POST http://localhost:{PORT}/chat \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"message": "北京明天的天气怎么样？"}\'')

    print("\nSSE 流式请求:")
    print(f'curl -X POST http://localhost:{PORT}/chat/stream \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "Accept: text/event-stream" \\')
    print('  -d \'{"message": "北京明天的天气怎么样？"}\'')
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")

#!/usr/bin/env python3
"""
06 - API Deployment
使用 FastAPI 部署天气智能体为 HTTP 服务
"""

import os
import json
import uvicorn
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from pydantic import SecretStr

# 加载环境变量
load_dotenv(override=True)

# 检查 API 密钥
if not os.getenv("OPENAI_API_KEY"):
    print("警告：请设置 OPENAI_API_KEY 环境变量")

# 导入 LangChain 组件
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.tools import tool
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    print("警告：LangChain 组件未安装，将使用模拟模式")

# 创建 FastAPI 应用
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

# 全局变量
agent_executor = None


# 请求/响应模型
class WeatherRequest(BaseModel):
    location: str
    days: int = 1


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class WeatherResponse(BaseModel):
    location: str
    date: str
    temperature: Dict[str, float]
    condition: str
    humidity: float
    wind_speed: float
    rain: bool


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    langchain_available: bool
    openai_configured: bool


# 模拟天气数据
def get_weather_data(location: str, days: int = 1) -> dict:
    """获取天气数据（模拟）"""
    weather_database = {
        "北京": {
            "temp_range": (15, 25),
            "conditions": ["晴", "多云", "小雨"],
            "humidity_range": (40, 70),
            "wind_range": (5, 15),
        },
        "上海": {
            "temp_range": (18, 28),
            "conditions": ["多云", "阴", "小雨"],
            "humidity_range": (60, 80),
            "wind_range": (10, 20),
        },
        "广州": {
            "temp_range": (22, 32),
            "conditions": ["晴", "多云", "雷阵雨"],
            "humidity_range": (70, 90),
            "wind_range": (5, 12),
        },
        "深圳": {
            "temp_range": (23, 31),
            "conditions": ["晴", "多云", "阵雨"],
            "humidity_range": (65, 85),
            "wind_range": (8, 15),
        },
    }

    city_data = weather_database.get(
        location,
        {
            "temp_range": (10, 20),
            "conditions": ["晴", "多云", "阴"],
            "humidity_range": (50, 70),
            "wind_range": (5, 15),
        },
    )

    weather_data = []
    base_date = datetime.now()

    import random

    for i in range(days):
        date = base_date + timedelta(days=i)
        temp_min, temp_max = city_data["temp_range"]
        humidity_min, humidity_max = city_data["humidity_range"]
        wind_min, wind_max = city_data["wind_range"]

        random.seed(hash(location + str(i)))

        day_data = {
            "date": date.strftime("%Y-%m-%d"),
            "location": location,
            "temperature": {
                "min": round(temp_min + random.uniform(-2, 2), 1),
                "max": round(temp_max + random.uniform(-2, 2), 1),
                "avg": round((temp_min + temp_max) / 2 + random.uniform(-1, 1), 1),
            },
            "condition": random.choice(city_data["conditions"]),
            "humidity": round(random.uniform(humidity_min, humidity_max), 1),
            "wind_speed": round(random.uniform(wind_min, wind_max), 1),
            "rain": random.choice([True, False])
            if "雨" in random.choice(city_data["conditions"])
            else False,
        }
        weather_data.append(day_data)

    return {"location": location, "days": days, "data": weather_data}


# 初始化智能体
def initialize_agent():
    """初始化天气智能体"""
    global agent_executor

    if not LANGCHAIN_AVAILABLE or not os.getenv("OPENAI_API_KEY"):
        print("智能体初始化跳过：LangChain 或 OpenAI 配置不完整")
        return

    try:

        @tool
        def get_weather(location: str, days: int = 1) -> str:
            """获取指定地点未来几天的天气信息。

            Args:
                location (str): 城市名称，如"北京"、"上海"
                days (int): 查询天数，默认1天，最多7天

            Returns:
                str: 天气信息的JSON格式字符串
            """
            days = min(max(days, 1), 7)

            try:
                weather_data = get_weather_data(location, days)
                return json.dumps(weather_data, ensure_ascii=False, indent=2)
            except Exception as e:
                return json.dumps(
                    {"error": f"获取天气数据失败：{str(e)}"}, ensure_ascii=False
                )

        # 从环境变量读取配置
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

        # 创建 LLM 和智能体
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(api_key),
            base_url=base_url,
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            你是一个专业的天气助手智能体。你能够：

            1. 获取指定城市的天气信息
            2. 分析天气数据并提供建议
            3. 根据天气情况给出穿衣、出行建议

            可用工具：
            - get_weather: 获取天气数据

            工作流程：
            1. 理解用户需求
            2. 获取相关天气数据
            3. 分析数据并提供建议

            请用中文回答，保持友好和专业的语调。
            """,
                ),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        tools = [get_weather]

        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)

        agent_executor = AgentExecutor(
            agent=agent, tools=tools, verbose=False, max_iterations=5
        )

        print("✓ 天气智能体初始化完成")

    except Exception as e:
        print(f"智能体初始化失败：{e}")
        agent_executor = None


# 启动时初始化
@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    initialize_agent()


# API 路由
@app.get("/", response_model=Dict[str, Any])
async def root():
    """根路径，返回 API 信息"""
    return {
        "message": "LangChain 天气智能体 API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "weather": "/weather",
            "chat": "/chat",
            "docs": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查"""
    return HealthResponse(
        status="healthy",
        langchain_available=LANGCHAIN_AVAILABLE,
        openai_configured=bool(os.getenv("OPENAI_API_KEY")),
    )


@app.post("/weather", response_model=Dict[str, Any])
async def get_weather_endpoint(request: WeatherRequest):
    """获取天气信息 API"""
    try:
        weather_data = get_weather_data(request.location, request.days)

        # 转换为响应格式
        response = {
            "location": weather_data["location"],
            "days": weather_data["days"],
            "forecast": [
                {
                    "date": day["date"],
                    "temperature": day["temperature"],
                    "condition": day["condition"],
                    "humidity": day["humidity"],
                    "wind_speed": day["wind_speed"],
                    "rain": day["rain"],
                }
                for day in weather_data["data"]
            ],
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取天气数据失败：{str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """智能体对话 API"""
    global agent_executor

    if not agent_executor:
        # 模拟响应
        simulated_responses = [
            f"关于'{request.message}'，我需要更多信息来帮助您。",
            f"我理解您想了解：{request.message}。请提供更具体的位置信息。",
            f"收到您的消息：{request.message}。我可以帮您查询天气信息。",
        ]

        import random

        response_text = random.choice(simulated_responses)
    else:
        try:
            # 使用智能体响应
            response = agent_executor.invoke({"input": request.message})
            response_text = response["output"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"智能体处理失败：{str(e)}")

    return ChatResponse(
        response=response_text,
        session_id=request.session_id or "default",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/weather/{location}", response_model=Dict[str, Any])
async def get_weather_by_location(location: str, days: int = 1):
    """通过路径参数获取天气信息"""
    if days < 1 or days > 7:
        raise HTTPException(status_code=400, detail="天数必须在 1-7 之间")

    weather_data = get_weather_data(location, days)

    return {
        "location": weather_data["location"],
        "days": weather_data["days"],
        "forecast": weather_data["data"],
    }


# 后台任务示例
async def process_weather_data(location: str):
    """后台处理天气数据"""
    # 这里可以添加复杂的数据处理逻辑
    await asyncio.sleep(2)  # 模拟处理时间
    print(f"后台处理完成：{location}")


@app.post("/weather-process/{location}")
async def process_weather_background(location: str, background_tasks: BackgroundTasks):
    """后台处理天气数据"""
    background_tasks.add_task(process_weather_data, location)
    return {"message": f"已开始处理 {location} 的天气数据"}


# 启动服务器
if __name__ == "__main__":
    import asyncio

    print("🚀 启动 LangChain 天气智能体 API 服务")
    print("=" * 50)
    print("API 文档：http://localhost:8000/docs")
    print("健康检查：http://localhost:8000/health")
    print("天气查询：http://localhost:8000/weather/北京")
    print("=" * 50)

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")

#!/usr/bin/env python3
"""
05 - Agent Weather (LangChain 1.0 版本)
使用 create_agent API 创建智能体，让 AI 能够使用工具获取实时天气信息
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


def main():
    print("🦜🔗 05 - Agent Weather (LangChain 1.0)")
    print("=" * 50)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import create_agent
        from langchain.tools import tool

        print("✓ LangChain 1.0 组件导入完成")

        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(api_key),
            base_url=base_url,
        )

        print("\n=== 1. 创建天气获取工具 ===")

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

            for i in range(days):
                date = base_date + timedelta(days=i)
                temp_min, temp_max = city_data["temp_range"]
                humidity_min, humidity_max = city_data["humidity_range"]
                wind_min, wind_max = city_data["wind_range"]

                import random

                random.seed(hash(location + str(i)))

                day_data = {
                    "date": date.strftime("%Y-%m-%d"),
                    "location": location,
                    "temperature": {
                        "min": round(temp_min + random.uniform(-2, 2), 1),
                        "max": round(temp_max + random.uniform(-2, 2), 1),
                        "avg": round(
                            (temp_min + temp_max) / 2 + random.uniform(-1, 1), 1
                        ),
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

        print("✓ 天气获取工具创建完成")

        print("\n=== 2. 使用 create_agent 创建智能体 ===")

        agent = create_agent(
            model=llm,
            tools=[get_weather],
            system_prompt="""
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
        )

        print("✓ 天气智能体创建完成")

        print("\n=== 3. 测试智能体 ===")

        test_questions = [
            "查询北京明天的天气情况",
            "上海未来3天天气怎么样？",
            "明天我需要带伞吗？我在广州",
        ]

        for question in test_questions:
            print(f"\n问题：{question}")
            try:
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": question}]}
                )
                print(f"回答：{result['messages'][-1].content}")

                print(f"消息流转数量：{len(result['messages'])}")
            except Exception as e:
                print(f"错误：{e}")

        print("\n=== 4. 天气数据分析演示 ===")

        weather_data = get_weather_data("北京", 3)
        print(f"\n{weather_data['location']} 未来 {weather_data['days']} 天天气：")

        for day in weather_data["data"]:
            print(f"\n日期：{day['date']}")
            print(f"温度：{day['temperature']['min']}-{day['temperature']['max']}°C")
            print(f"天气：{day['condition']}")
            print(f"湿度：{day['humidity']}%")
            print(f"风速：{day['wind_speed']} km/h")
            print(f"降雨：{'是' if day['rain'] else '否'}")

        print("\n🎉 Agent Weather (LangChain 1.0) 示例运行成功！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

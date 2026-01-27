#!/usr/bin/env python3
"""
05 - Agent Weather
使用 create_agent API 创建智能体，让 AI 能够使用工具获取实时天气信息
"""

import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)


def main():
    print("🦜🔗 05 - Agent Weather")
    print("=" * 50)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    if not os.getenv("OPENWEATHER_API_KEY"):
        print("❌ 请设置 OPENWEATHER_API_KEY 环境变量")
        return 1

    try:
        from langchain.agents import create_agent
        from langchain.tools import tool

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from clients import create_model_client

        print("✓ LangChain 组件导入完成")

        llm = create_model_client(temperature=0)

        print("\n=== 1. 创建天气获取工具 ===")

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

        print("✓ 天气获取工具创建完成")

        print("\n=== 2. 使用 create_agent 创建智能体 ===")

        agent = create_agent(
            model=llm,
            tools=[get_weather],
            system_prompt="""你是一个专业的天气助手智能体。你能够：

1. 获取指定城市的天气信息
2. 分析天气数据并提供建议
3. 根据天气情况给出穿衣、出行建议

可用工具：
- get_weather: 获取天气数据

工作流程：
1. 理解用户需求
2. 获取相关天气数据
3. 分析数据并提供建议

请用中文回答，保持友好和专业的语调。""",
        )

        print("✓ 天气智能体创建完成")

        print("\n=== 3. 测试智能体 ===")

        questions = [
            "北京明天的天气怎么样？",
            "上海需要带伞吗？",
        ]

        for question in questions:
            print(f"\n用户问题: {question}")
            print("-" * 50)

            try:
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": question}]}
                )

                answer = result["messages"][-1].content
                print("最终回答:")
                print(f"  {answer}")
                print(f"消息流转数量: {len(result['messages'])}")
            except Exception as e:
                print(f"错误：{e}")

            print("=" * 50)

        print("\n🎉 Agent Weather 示例运行成功！")

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

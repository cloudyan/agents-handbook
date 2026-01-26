#!/usr/bin/env python3
"""
API 测试脚本
测试天气智能体 API 的各个端点
"""

import requests
import json
import time
from typing import Dict, Any

# API 基础 URL
BASE_URL = "http://localhost:8000"


def test_health():
    """测试健康检查端点"""
    print("=== 测试健康检查 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码：{response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"服务状态：{data['status']}")
            print(f"LangChain 可用：{data['langchain_available']}")
            print(f"OpenAI 配置：{data['openai_configured']}")
        else:
            print(f"错误：{response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    print()


def test_weather_api():
    """测试天气 API"""
    print("=== 测试天气 API ===")

    # 测试北京天气
    try:
        response = requests.get(f"{BASE_URL}/weather/北京")
        print(f"状态码：{response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"地点：{data['location']}")
            print(f"天数：{data['days']}")
            print("天气预报：")
            for day in data["forecast"]:
                print(
                    f"  {day['date']}: {day['temperature']['min']}-{day['temperature']['max']}°C, {day['condition']}"
                )
        else:
            print(f"错误：{response.text}")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    print()


def test_weather_post():
    """测试 POST 天气 API"""
    print("=== 测试 POST 天气 API ===")

    payload = {"location": "上海", "days": 3}

    try:
        response = requests.post(
            f"{BASE_URL}/weather",
            json=payload,
            headers={"Content-Type": "application/json"},
        )
        print(f"状态码：{response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"地点：{data['location']}")
            print(f"预报天数：{len(data['forecast'])}")
            for day in data["forecast"]:
                print(f"  {day['date']}: {day['condition']}, 湿度 {day['humidity']}%")
        else:
            print(f"错误：{response.text}")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    print()


def test_chat_api():
    """测试聊天 API"""
    print("=== 测试聊天 API ===")

    questions = ["北京明天天气怎么样？", "我需要带伞吗？", "上海未来3天天气如何？"]

    for question in questions:
        payload = {"message": question, "session_id": "test_session"}

        try:
            response = requests.post(
                f"{BASE_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            print(f"问题：{question}")
            print(f"状态码：{response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"回答：{data['response']}")
                print(f"会话ID：{data['session_id']}")
            else:
                print(f"错误：{response.text}")
            print()

        except Exception as e:
            print(f"❌ 测试失败：{e}")
            print()


def test_background_task():
    """测试后台任务"""
    print("=== 测试后台任务 ===")

    try:
        response = requests.post(f"{BASE_URL}/weather-process/广州")
        print(f"状态码：{response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应：{data['message']}")
            print("后台任务已启动，等待2秒...")
            time.sleep(2)
        else:
            print(f"错误：{response.text}")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    print()


def test_error_handling():
    """测试错误处理"""
    print("=== 测试错误处理 ===")

    # 测试无效的天数
    try:
        response = requests.get(f"{BASE_URL}/weather/北京?days=10")
        print(f"无效天数测试 - 状态码：{response.status_code}")
        if response.status_code == 400:
            print("✓ 正确处理了无效天数参数")
        else:
            print("❌ 未正确处理无效参数")
    except Exception as e:
        print(f"❌ 测试失败：{e}")

    # 测试不存在的端点
    try:
        response = requests.get(f"{BASE_URL}/invalid")
        print(f"无效端点测试 - 状态码：{response.status_code}")
        if response.status_code == 404:
            print("✓ 正确返回了 404 错误")
        else:
            print("❌ 未正确处理无效端点")
    except Exception as e:
        print(f"❌ 测试失败：{e}")
    print()


def main():
    """运行所有测试"""
    print("🧪 LangChain 天气智能体 API 测试")
    print("=" * 50)
    print("请确保服务器正在运行：python main.py")
    print()

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)

    # 运行测试
    test_health()
    test_weather_api()
    test_weather_post()
    test_chat_api()
    test_background_task()
    test_error_handling()

    print("🎉 API 测试完成！")
    print("\n📚 更多信息：")
    print("- API 文档：http://localhost:8000/docs")
    print("- 交互式文档：http://localhost:8000/redoc")


if __name__ == "__main__":
    main()

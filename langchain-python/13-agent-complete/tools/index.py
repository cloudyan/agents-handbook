import os
import httpx
from langchain_core.tools import tool


@tool
def get_weather(location: str, days: int = 1) -> str:
    """
    获取指定城市的天气预报，包括温度、天气状况和降雨概率。
    输入应该是城市的英文名称。

    Args:
        location: 城市英文名称，例如 Beijing, Shanghai, New York
        days: 预报天数，默认为1天

    Returns:
        天气预报信息
    """
    try:
        weather_api_key = os.getenv("OPENWEATHER_API_KEY")

        if not weather_api_key:
            return "天气查询功能需要配置 OPENWEATHER_API_KEY 环境变量"

        url = f"https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": location,
            "appid": weather_api_key,
            "units": "metric",
            "cnt": days * 8,
        }

        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        forecasts = data["list"][: days * 8]
        result = f"{location} 天气预报：\n"

        for item in forecasts:
            date = item["dt"]
            weather_desc = item["weather"][0]["description"]
            temp = item["main"]["temp"]
            humidity = item["main"]["humidity"]
            result += f"{date} {weather_desc}, 温度: {temp}°C, 湿度: {humidity}%\n"

        return result

    except Exception as e:
        return f"获取天气失败: {str(e)}"


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    搜索网络信息，获取最新的资讯和数据。适用于需要实时信息的问题。

    Args:
        query: 搜索关键词
        max_results: 返回结果数量，默认为5

    Returns:
        搜索结果
    """
    try:
        tavily_api_key = os.getenv("TAVILY_API_KEY")

        if not tavily_api_key:
            return "网络搜索功能需要配置 TAVILY_API_KEY 环境变量"

        url = "https://api.tavily.com/search"
        payload = {
            "api_key": tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()

        results = data["results"]
        result = "🔍 搜索结果：\n"

        for index, item in enumerate(results, 1):
            result += f"{index}. {item['title']}\n"
            result += f"   {item['url']}\n"
            result += f"   {item['content']}\n\n"

        return result

    except Exception as e:
        return f"搜索失败: {str(e)}"


@tool
def calculate(expression: str) -> str:
    """
    计算数学表达式，支持加减乘除和括号。

    Args:
        expression: 数学表达式，如 2 + 3 * 4 或 (10 + 5) / 3

    Returns:
        计算结果
    """
    try:
        sanitized = "".join(c for c in expression if c in "0123456789+-*/(). ")
        result = eval(sanitized)
        return f"计算结果：{expression} = {result}"

    except Exception:
        return "计算错误，请检查表达式格式。支持 +、-、*、/ 和括号"


@tool
def get_current_time() -> str:
    """
    获取当前的日期和时间。

    Returns:
        当前时间字符串
    """
    from datetime import datetime

    now = datetime.now()
    return f"当前时间：{now.strftime('%Y年%m月%d日 %H:%M:%S')}"


tools = [get_weather, search_web, calculate, get_current_time]

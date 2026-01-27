"""Tavily 搜索客户端模块"""
import os
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv(override=True)


@tool
def create_tavily_search_tool(api_key: str):
    """创建 Tavily 搜索工具

    Args:
        api_key: Tavily API 密钥

    Returns:
        Tavily 搜索工具函数
    """

    async def search(query: str) -> str:
        """使用 Tavily API 进行网络搜索

        Args:
            query: 搜索查询关键词

        Returns:
            搜索结果字符串
        """
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 5,
                        "include_answer": True,
                        "include_images": False,
                        "include_image_descriptions": False,
                        "include_raw_content": False,
                    },
                    timeout=30.0,
                )

                if response.status_code != 200:
                    raise Exception(f"Tavily API error: {response.status_code}")

                data = response.json()

                search_results = "\n\n".join(
                    [
                        f"{i + 1}. {result['title']}\n   URL: {result['url']}\n   内容: {result['content'][:300]}..."
                        for i, result in enumerate(data.get("results", []))
                    ]
                )

                return f"搜索结果：\n\n{search_results}\n\nAI 总结：{data.get('answer', '无总结')}"
        except Exception as e:
            print(f"Tavily search error: {e}")
            return f"搜索失败：{str(e)}"

    return search


def create_mock_search_tool():
    """创建模拟搜索工具（用于测试）"""

    @tool
    def search_database(query: str) -> str:
        """搜索工具（模拟）

        Args:
            query: 搜索查询

        Returns:
            搜索结果
        """
        knowledge_base = {
            "快速排序": "快速排序是一种分治算法，平均时间复杂度 O(n log n)，通过选择基准元素分区实现。",
            "Python": "Python 是一种高级编程语言，语法简洁，适合快速开发。",
            "算法": "算法是解决特定问题的一系列明确步骤。",
            "代码优化": "代码优化包括时间复杂度优化、空间复杂度优化、代码可读性提升等。",
            "JavaScript": "JavaScript 是一种动态编程语言，主要用于 Web 开发，支持事件驱动和函数式编程。",
            "React": "React 是一个用于构建用户界面的 JavaScript 库，由 Facebook 开发，采用组件化架构。",
            "Vue": "Vue.js 是一个渐进式 JavaScript 框架，易于上手，支持双向数据绑定和组件化开发。",
            "Node.js": "Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时，用于构建服务器端应用。",
            "TypeScript": "TypeScript 是 JavaScript 的超集，添加了静态类型检查，提高代码可维护性。",
        }

        for key, value in knowledge_base.items():
            if key in query:
                return f"找到：{value}"

        return f"关于 '{query}' 的搜索结果：建议查阅官方文档和技术博客。"

    return search_database


def create_search_tool():
    """创建搜索工具，自动选择 Tavily 或模拟工具

    Returns:
        搜索工具
    """
    tavily_api_key = os.getenv("TAVILY_API_KEY")

    if tavily_api_key and tavily_api_key != "your_tavily_api_key_here" and len(tavily_api_key) > 10:
        print("✓ 使用 Tavily 搜索 API")
        return create_tavily_search_tool(tavily_api_key)
    else:
        print("⚠ Tavily API Key 未配置，使用模拟搜索工具")
        return create_mock_search_tool()

"""客户端模块"""

import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


def create_model_client(temperature=0):
    """创建模型客户端"""
    from langchain_openai import ChatOpenAI
    
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        api_key=SecretStr(openai_api_key),
        base_url=openai_base_url,
    )


def create_search_tool():
    """创建搜索工具"""
    from langchain.tools import tool
    
    @tool
    def search_tool(query: str) -> str:
        """搜索工具（模拟）"""
        knowledge_base = {
            "快速排序": "快速排序是一种分治算法，平均时间复杂度 O(n log n)，通过选择基准元素分区实现。",
            "Python": "Python 是一种高级编程语言，语法简洁，适合快速开发。",
            "算法": "算法是解决特定问题的一系列明确步骤。",
            "代码优化": "代码优化包括时间复杂度优化、空间复杂度优化、代码可读性提升等。",
            "React": "React 是一个用于构建用户界面的 JavaScript 库。",
            "Vue": "Vue 是一个渐进式 JavaScript 框架。",
            "JavaScript": "JavaScript 是一种动态编程语言，主要用于 Web 开发。",
            "TypeScript": "TypeScript 是 JavaScript 的超集，添加了静态类型。",
            "机器学习": "机器学习是人工智能的一个分支，让计算机能够从数据中学习。",
            "深度学习": "深度学习是机器学习的一个子集，使用神经网络。",
        }
        
        for key, value in knowledge_base.items():
            if key in query:
                return f"找到：{value}"
        
        return f"关于 '{query}' 的搜索结果：建议查阅官方文档和技术博客。"
    
    return search_tool

#!/usr/bin/env python3
"""
07 - Advanced Agents (LangChain 1.0 版本)
高级Agent模式示例：ReAct、Self-Ask、Plan-and-Execute 使用 create_agent API
"""

import os
import json
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


def main():
    print("🦜🔗 07 - Advanced Agents (LangChain 1.0)")
    print("=" * 60)

    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    if not openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import create_agent
        from langchain.tools import tool

        print("✓ LangChain 1.0 高级组件导入完成")

        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url,
        )

        print("\n=== 1. ReAct Agent 示例 ===")

        @tool
        def search_database(query: str) -> str:
            """搜索数据库中的信息。

            Args:
                query (str): 搜索查询字符串

            Returns:
                str: 搜索结果
            """
            database = {
                "Python": "Python 是一种高级编程语言，由 Guido van Rossum 创建。",
                "机器学习": "机器学习是人工智能的一个分支，让计算机能够从数据中学习。",
                "LangChain": "LangChain 是用于构建 LLM 应用的框架。",
                "React": "React 是一个用于构建用户界面的 JavaScript 库。",
            }

            for key, value in database.items():
                if query.lower() in key.lower():
                    return f"找到信息：{value}"

            return "未找到相关信息"

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

        react_agent = create_agent(
            model=llm,
            tools=[search_database, calculate],
            system_prompt="""
你是一个智能助手，能够回答复杂问题。对于复杂问题，你会：

1. 分析问题需要哪些信息
2. 使用工具获取必要信息
3. 进行计算或推理
4. 综合得出最终答案

可用工具：
- search_database: 搜索数据库信息
- calculate: 计算数学表达式

请按照思考-行动-观察的流程来回答问题。
""",
        )

        print("测试 ReAct Agent:")
        questions = [
            "Python 是什么？再计算一下 15 + 27 等于多少？",
            "React 是什么？计算一下 8 * 9 + 5",
        ]

        for question in questions:
            print(f"\n问题：{question}")
            result = react_agent.invoke(
                {"messages": [{"role": "user", "content": question}]}
            )
            print(f"回答：{result['messages'][-1].content}")
            print(f"消息流转：{len(result['messages'])} 步")

        print("\n=== 2. Self-Ask Agent 示例 ===")

        @tool
        def web_search(query: str) -> str:
            """模拟网络搜索。

            Args:
                query (str): 搜索查询

            Returns:
                str: 搜索结果
            """
            search_results = {
                "LangChain 创建者": "LangChain 由 Harrison Chase 创建。",
                "LangChain 首次发布": "LangChain 于 2022 年首次发布。",
                "LangChain 功能": "LangChain 提供了 LLM 抽象、提示词管理、链式调用等功能。",
                "LangChain 版本": "LangChain 1.0 统一了 Agent API，引入了 LangGraph。",
            }

            for key, value in search_results.items():
                if query.lower() in key.lower():
                    return value

            return f"关于 '{query}' 的搜索结果：未找到具体信息"

        self_ask_agent = create_agent(
            model=llm,
            tools=[web_search],
            system_prompt="""
你是一个智能助手，能够回答复杂问题。对于复杂问题，你会将其分解为子问题。

策略：
1. 识别问题中的关键信息需求
2. 将复杂问题分解为多个子问题
3. 逐步搜索答案
4. 综合得出最终答案

可用工具：
- web_search: 搜索网络信息

请用简洁明了的方式回答。
""",
        )

        print("\n测试 Self-Ask Agent:")
        self_ask_questions = [
            "LangChain 是谁创建的？什么时候发布的？有什么功能？",
        ]

        for question in self_ask_questions:
            print(f"\n问题：{question}")
            result = self_ask_agent.invoke(
                {"messages": [{"role": "user", "content": question}]}
            )
            print(f"回答：{result['messages'][-1].content}")

        print("\n=== 3. Plan-and-Execute 模式示例 ===")

        plan_execute_agent = create_agent(
            model=llm,
            tools=[search_database, calculate, web_search],
            system_prompt="""
你是一个任务规划与执行专家。对于复杂任务，你会：

1. **规划阶段**：分析任务，制定详细的执行计划
2. **执行阶段**：按照计划逐步执行
3. **总结阶段**：汇总结果，提供最终答案

可用工具：
- search_database: 搜索数据库信息
- calculate: 计算数学表达式
- web_search: 搜索网络信息

执行流程：
- 首先分析任务需求
- 制定执行计划
- 按计划执行
- 汇总结果

请提供清晰的执行计划和结果。
""",
        )

        print("\n测试 Plan-and-Execute Agent:")
        plan_questions = [
            "研究 Python 编程语言的特点，并计算 25 * 4 的结果",
        ]

        for question in plan_questions:
            print(f"\n问题：{question}")
            result = plan_execute_agent.invoke(
                {"messages": [{"role": "user", "content": question}]}
            )
            print(f"回答：{result['messages'][-1].content}")

        print("\n=== 4. Agent 性能对比 ===")

        comparison_questions = [
            "什么是 Python？",
            "计算 25 * 4 等于多少？",
            "搜索 LangChain 的信息",
        ]

        agents = {
            "ReAct Agent": react_agent,
            "Self-Ask Agent": self_ask_agent,
            "Plan-Execute Agent": plan_execute_agent,
        }

        print("\n性能对比测试：")
        for agent_name, agent in agents.items():
            print(f"\n--- {agent_name} ---")
            for question in comparison_questions:
                try:
                    result = agent.invoke(
                        {"messages": [{"role": "user", "content": question}]}
                    )
                    print(f"Q: {question}")
                    print(f"A: {result['messages'][-1].content[:100]}...")
                    print(f"Steps: {len(result['messages'])}")
                except Exception as e:
                    print(f"错误：{e}")

        print("\n🎉 高级 Agent (LangChain 1.0) 示例运行完成！")

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

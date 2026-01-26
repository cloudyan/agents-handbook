#!/usr/bin/env python3
"""
07 - Advanced Agents
高级Agent模式示例：ReAct、Self-Ask、Plan-and-Execute
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv
from pydantic import SecretStr

# 加载环境变量
load_dotenv(override=True)


def main():
    print("🦜🔗 07 - Advanced Agents")
    print("=" * 50)

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    # 检查 API 密钥
    if not openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        # 导入 LangChain 组件
        from langchain_openai import ChatOpenAI
        from langchain.agents import (
            tool,
            AgentExecutor,
            create_react_agent,
            create_self_ask_with_search_agent,
        )
        from langchain_core.prompts import PromptTemplate

        print("✓ LangChain 高级组件导入完成")

        # 初始化 LLM（使用 SecretStr 包装 API key）
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )

        # 1. ReAct Agent 示例
        print("\n=== 1. ReAct Agent 示例 ===")

        @tool
        def search_database(query: str) -> str:
            """搜索数据库中的信息。

            Args:
                query (str): 搜索查询字符串

            Returns:
                str: 搜索结果
            """
            # 模拟数据库搜索
            database = {
                "Python": "Python 是一种高级编程语言，由 Guido van Rossum 创建。",
                "机器学习": "机器学习是人工智能的一个分支，让计算机能够从数据中学习。",
                "LangChain": "LangChain 是用于构建 LLM 应用的框架。",
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
                # 简单的数学表达式计算（注意：实际应用中需要更安全的实现）
                result = eval(expression)
                return f"计算结果：{result}"
            except:
                return "计算错误，请检查表达式"

        # 创建 ReAct 提示词
        react_prompt = PromptTemplate.from_template("""
        回答以下问题，你可以使用这些工具：

        {tools}

        使用以下格式：

        Question: 需要回答的问题
        Thought: 你应该思考要做什么
        Action: 要采取的行动，应该是 [{tool_names}] 中的一个
        Action Input: 行动的输入
        Observation: 行动的结果
        ... (这个 Thought/Action/Action Input/Observation 可以重复)
        Thought: 我现在知道最终答案了
        Final Answer: 对原始问题的最终答案

        开始！

        Question: {input}
        Thought: {agent_scratchpad}
        """)

        # 创建 ReAct Agent
        tools = [search_database, calculate]

        react_agent = create_react_agent(llm, tools, react_prompt)
        react_executor = AgentExecutor(agent=react_agent, tools=tools, verbose=True)

        # 测试 ReAct Agent
        print("测试 ReAct Agent:")
        react_response = react_executor.invoke(
            {"input": "Python 是什么？再计算一下 15 + 27 等于多少？"}
        )
        print(f"ReAct 回答：{react_response['output']}")

        # 2. Self-Ask Agent 示例
        print("\n=== 2. Self-Ask Agent 示例 ===")

        # 创建模拟搜索工具
        @tool
        def web_search(query: str) -> str:
            """模拟网络搜索。

            Args:
                query (str): 搜索查询

            Returns:
                str: 搜索结果
            """
            # 模拟搜索结果
            search_results = {
                "LangChain 创建者": "LangChain 由 Harrison Chase 创建。",
                "LangChain 首次发布": "LangChain 于 2022 年首次发布。",
                "LangChain 功能": "LangChain 提供了 LLM 抽象、提示词管理、链式调用等功能。",
            }

            for key, value in search_results.items():
                if query.lower() in key.lower():
                    return value

            return f"关于 '{query}' 的搜索结果：未找到具体信息"

        # 创建 Self-Ask 提示词
        self_ask_prompt = PromptTemplate.from_template("""
        你是一个智能助手，能够回答复杂问题。对于复杂问题，你会将其分解为子问题。

        Question: {input}
        """)

        # 注意：实际的 Self-Ask Agent 需要特定的搜索工具配置
        # 这里提供一个简化版本
        print("Self-Ask Agent 需要特定的搜索配置，这里展示概念：")
        print("1. 将复杂问题分解为子问题")
        print("2. 逐步搜索答案")
        print("3. 综合得出最终答案")

        # 3. Plan-and-Execute 模式示例
        print("\n=== 3. Plan-and-Execute 模式示例 ===")

        class PlanExecuteAgent:
            """简化的 Plan-and-Execute Agent 实现"""

            def __init__(self, llm, tools):
                self.llm = llm
                self.tools = {tool.name: tool for tool in tools}
                self.planner_prompt = PromptTemplate.from_template("""
                给定一个目标，制定一个详细的执行计划。列出需要执行的步骤。

                目标：{goal}

                可用工具：{tool_names}

                请制定执行计划：
                """)

                self.executor_prompt = PromptTemplate.from_template("""
                执行计划中的下一步。

                当前步骤：{step}
                之前的结果：{previous_results}

                请执行这一步：
                """)

            def plan(self, goal: str) -> List[str]:
                """制定执行计划"""
                tool_names = ", ".join(self.tools.keys())
                prompt = self.planner_prompt.format(goal=goal, tool_names=tool_names)

                response = self.llm.invoke(prompt)
                # 简化：假设返回的是步骤列表
                return ["搜索相关信息", "分析数据", "生成报告"]

            def execute(self, plan: List[str]) -> str:
                """执行计划"""
                results = []

                for step in plan:
                    print(f"执行步骤：{step}")

                    if "搜索" in step:
                        result = self.tools["search_database"].invoke("Python")
                    elif "计算" in step:
                        result = self.tools["calculate"].invoke("10 + 20")
                    else:
                        result = f"完成步骤：{step}"

                    results.append(result)
                    print(f"结果：{result}")

                return "\n".join(results)

            def run(self, goal: str) -> str:
                """运行完整的 Plan-and-Execute 流程"""
                print(f"目标：{goal}")

                # 1. 制定计划
                plan = self.plan(goal)
                print(f"制定的计划：{plan}")

                # 2. 执行计划
                result = self.execute(plan)

                return f"计划执行完成：\n{result}"

        # 创建并测试 Plan-and-Execute Agent
        plan_execute_agent = PlanExecuteAgent(llm, tools)
        plan_result = plan_execute_agent.run("研究 Python 并进行相关计算")
        print(f"\nPlan-and-Execute 结果：\n{plan_result}")

        # 4. Agent 性能对比
        print("\n=== 4. Agent 性能对比 ===")

        comparison_questions = [
            "什么是 Python？",
            "计算 25 * 4 等于多少？",
            "搜索 LangChain 的信息",
        ]

        agents = {
            "ReAct": react_executor,
            # 可以添加其他 Agent 进行对比
        }

        for agent_name, agent in agents.items():
            print(f"\n--- {agent_name} Agent 测试 ---")
            for question in comparison_questions:
                try:
                    response = agent.invoke({"input": question})
                    print(f"Q: {question}")
                    print(f"A: {response['output'][:100]}...")
                except Exception as e:
                    print(f"错误：{e}")

        print("\n🎉 高级 Agent 示例运行完成！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

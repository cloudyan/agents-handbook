#!/usr/bin/env python3
"""
07 - Advanced Agents (LangChain 1.0 版本)
高级Agent模式示例：ReAct、Self-Ask、Plan-and-Execute 使用 create_agent API
"""

import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


class PlanExecuteAgent:
    """Plan-and-Execute 模式的自定义实现"""

    def __init__(self, model, tools: List[Dict[str, Any]]):
        self.model = model
        self.tools = {tool["name"]: tool for tool in tools}
        self.tool_call_count = 0

    def get_tool_call_count(self) -> int:
        return self.tool_call_count

    def reset_tool_call_count(self) -> None:
        self.tool_call_count = 0

    def plan(self, goal: str) -> List[str]:
        """规划阶段：制定执行计划"""
        tool_names = ", ".join(self.tools.keys())
        prompt = f"""给定一个目标，制定一个简洁的执行计划。只列出需要执行的关键步骤，每个步骤一行。

目标：{goal}

可用工具：{tool_names}

请按以下格式输出，只包含步骤编号和步骤描述：
1. 第一步
2. 第二步
3. 第三步

执行计划："""

        response = self.model.invoke(prompt)
        content = response.content

        steps = []
        for line in content.split("\n"):
            line = line.strip()
            if line and len(line) > 5 and len(line) < 100:
                step = line.replace(r"^\d+[\.\、]\s*", "").strip()
                if step:
                    steps.append(step)

        if len(steps) == 0:
            steps = ["分析问题需求", "使用工具获取信息", "整理答案"]

        return steps[:5]

    def execute(self, plan: List[str], goal: str) -> str:
        """执行阶段：按照计划执行"""
        tool_results = []
        goal_lower = goal.lower()

        for step in plan:
            step_lower = step.lower()

            if any(keyword in step_lower for keyword in ["搜索", "search", "查询"]):
                if "search_database" in self.tools:
                    self.tool_call_count += 1
                    search_tool = self.tools["search_database"]["function"]

                    if "python" in goal_lower:
                        query = "Python"
                    elif "langchain" in goal_lower:
                        query = "LangChain"
                    else:
                        query = goal.replace("搜索", "").replace("查询", "").replace("信息", "").replace("是什么", "").replace("等", "").strip()

                    result = search_tool.invoke({"query": query})
                    tool_results.append(result)

            elif any(keyword in step_lower for keyword in ["计算", "calculate"]) or \
                 any(char in goal for char in ["+", "-", "*", "/"]):
                if "calculate" in self.tools:
                    self.tool_call_count += 1
                    calc_tool = self.tools["calculate"]["function"]

                    import re
                    expr_match = re.search(r'\d+[\+\-\*/]\d+', goal)
                    expr = expr_match.group(0) if expr_match else goal.replace("计算", "").replace("等于", "").replace("等", "").strip()

                    result = calc_tool.invoke({"expression": expr})
                    tool_results.append(result)

        if len(tool_results) == 0:
            return "根据现有知识直接回答问题。"

        answer_prompt = f"""根据以下工具执行结果，生成最终答案：

目标：{goal}
工具结果：
{chr(10).join([f"{i+1}. {r}" for i, r in enumerate(tool_results)])}

请提供简洁、准确的答案："""

        final_response = self.model.invoke(answer_prompt)
        return final_response.content

    def run(self, goal: str) -> Dict[str, Any]:
        """运行 Plan-and-Execute 流程"""
        self.reset_tool_call_count()

        plan = self.plan(goal)
        result = self.execute(plan, goal)

        return {
            "result": f"计划执行完成：\n{result}",
            "steps": plan
        }


def print_comparison_table(comparison_questions: List[str],
                         react_results: List[Dict[str, Any]],
                         plan_results: List[Dict[str, Any]]):
    """打印性能对比表格"""
    print("\n┌─────────────────────┬──────────────────┬──────────────────┬──────────────┬──────────────┐")
    print("│ 问题                │ ReAct 工具调用    │ Plan 工具调用    │ ReAct 成功率  │ Plan 成功率  │")
    print("├─────────────────────┼──────────────────┼──────────────────┼──────────────┼──────────────┤")

    for i, question in enumerate(comparison_questions):
        react = react_results[i]
        plan = plan_results[i]

        q = question[:19].ljust(19)
        react_calls = str(react["tool_calls"]).ljust(16)
        plan_calls = str(plan["tool_calls"]).ljust(16)
        react_success = "✓ 成功".ljust(12) if react["success"] else "✗ 失败".ljust(12)
        plan_success = "✓ 成功" if plan["success"] else "✗ 失败"

        print(f"│ {q} │ {react_calls} │ {plan_calls} │ {react_success} │ {plan_success} │")

    print("└─────────────────────┴──────────────────┴──────────────────┴──────────────┴──────────────┘")

    react_total_calls = sum(r["tool_calls"] for r in react_results)
    plan_total_calls = sum(r["tool_calls"] for r in plan_results)
    react_success_rate = sum(1 for r in react_results if r["success"]) / len(react_results) * 100
    plan_success_rate = sum(1 for r in plan_results if r["success"]) / len(plan_results) * 100

    print(f"\n📊 统计汇总：")
    print(f"   ReAct Agent: 总工具调用 {react_total_calls} 次, 成功率 {react_success_rate:.0f}%")
    print(f"   Plan Agent:  总工具调用 {plan_total_calls} 次, 成功率 {plan_success_rate:.0f}%")
    print(f"   效率对比: {'ReAct 更高效' if react_total_calls < plan_total_calls else 'Plan 更高效'}")


def print_detailed_comparison(comparison_questions: List[str],
                            react_results: List[Dict[str, Any]],
                            plan_results: List[Dict[str, Any]]):
    """打印详细的答案对比"""
    print("\n=== 5. 详细答案对比 ===\n")

    for i, question in enumerate(comparison_questions):
        print(f"📌 问题 {i+1}: {question}")
        print(f"\n  [ReAct]")
        react_answer = react_results[i]["answer"]
        print(f"  {react_answer[:150]}{'...' if len(react_answer) > 150 else ''}")
        print(f"\n  [Plan-and-Execute]")
        plan_answer = plan_results[i]["answer"]
        print(f"  {plan_answer[:150]}{'...' if len(plan_answer) > 150 else ''}")
        if plan_results[i].get("steps"):
            print(f"  步骤: {' → '.join(plan_results[i]['steps'])}")
        print()


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

        print("\n=== 1. ReAct 模式示例 ===")

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
            system_prompt="""你是一个智能助手，可以使用工具来帮助用户回答问题。请根据用户的问题，决定是否需要调用工具，并给出最终答案。请用中文回答问题。""",
        )

        react_response = react_agent.invoke({
            "messages": [{"role": "user", "content": "Python 是什么？再计算一下 15 + 27 等于多少？"}]
        })
        print(f"ReAct 回答：{react_response['messages'][-1].content}")

        print("\n=== 2. Plan-and-Execute 模式示例 ===")

        plan_execute_agent = PlanExecuteAgent(llm, [
            {"name": "search_database", "function": search_database},
            {"name": "calculate", "function": calculate}
        ])

        plan_result = plan_execute_agent.run("研究 Python 并进行相关计算")
        print(f"\nPlan-and-Execute 结果：\n{plan_result['result']}")
        print(f"执行步骤：{' → '.join(plan_result['steps'])}")

        print("\n=== 3. Self-Ask Agent 示例 ===")

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
            system_prompt="""你是一个智能助手，能够回答复杂问题。对于复杂问题，你会将其分解为子问题。

策略：
1. 识别问题中的关键信息需求
2. 将复杂问题分解为多个子问题
3. 逐步搜索答案
4. 综合得出最终答案

可用工具：
- web_search: 搜索网络信息

请用简洁明了的方式回答。""",
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

        print("\n=== 4. Agent 性能对比 ===")
        comparison_questions = [
            "什么是 Python？",
            "计算 25 * 4 等于多少？",
            "搜索 LangChain 的信息",
        ]

        react_results = []
        plan_results = []

        print("\n--- ReAct Agent 测试 ---")
        for question in comparison_questions:
            try:
                response = react_agent.invoke({
                    "messages": [{"role": "user", "content": question}]
                })
                content = response['messages'][-1].content

                import re
                tool_call_pattern = r'调用工具|使用工具|Tool call'
                tool_calls = len(re.findall(tool_call_pattern, content, re.IGNORECASE))

                react_results.append({
                    "question": question,
                    "answer": content,
                    "tool_calls": tool_calls,
                    "success": len(content) > 10
                })

                print(f"✓ {question}")
            except Exception as e:
                react_results.append({
                    "question": question,
                    "answer": f"错误：{str(e)}",
                    "tool_calls": 0,
                    "success": False
                })
                print(f"✗ {question}")

        print("\n--- Plan-and-Execute Agent 测试 ---")
        for question in comparison_questions:
            try:
                result = plan_execute_agent.run(question)

                plan_results.append({
                    "question": question,
                    "answer": result['result'],
                    "tool_calls": plan_execute_agent.get_tool_call_count(),
                    "success": len(result['result']) > 10,
                    "steps": result['steps']
                })

                print(f"✓ {question}")
            except Exception as e:
                plan_results.append({
                    "question": question,
                    "answer": f"错误：{str(e)}",
                    "tool_calls": 0,
                    "success": False
                })
                print(f"✗ {question}")

        print_comparison_table(comparison_questions, react_results, plan_results)
        print_detailed_comparison(comparison_questions, react_results, plan_results)

        print("\n高级 Agent 示例运行完成！")

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

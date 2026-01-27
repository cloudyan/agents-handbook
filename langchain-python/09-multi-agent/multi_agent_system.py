#!/usr/bin/env python3
"""
09 - 多智能体协作系统 (LangChain 1.0 版本)
使用 LangGraph + create_agent 实现 Supervisor 模式
"""

import os
from typing import TypedDict, Annotated, Sequence
from dotenv import load_dotenv
from pydantic import SecretStr
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import InMemorySaver
import operator

load_dotenv(override=True)


class AgentState(TypedDict):
    """智能体状态"""
    messages: Annotated[Sequence, operator.add]
    next_agent: str
    task_result: str


def main():
    print("🦜🔗 09 - 多智能体协作系统 (LangChain 1.0)")
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

        print("✓ LangChain 1.0 + LangGraph 组件导入完成")

        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url,
        )

        print("\n=== 1. 创建工具 ===")

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
            }

            for key, value in knowledge_base.items():
                if key in query:
                    return f"找到：{value}"

            return f"关于 '{query}' 的搜索结果：建议查阅官方文档和技术博客。"

        print("✓ 工具创建完成")

        print("\n=== 2. 创建专业 Agent ===")

        researcher_agent = create_agent(
            model=llm,
            tools=[search_tool],
            system_prompt="""
你是一个专业的研究助手，擅长：
1. 搜集和分析信息
2. 研究技术文档
3. 总结关键发现
4. 提供深入见解

请基于搜集的信息提供详细、准确的研究报告。
""",
        )

        coder_agent = create_agent(
            model=llm,
            tools=[search_tool],
            system_prompt="""
你是一个专业的程序员，擅长：
1. 编写高质量的代码
2. 遵循最佳实践
3. 添加清晰的注释
4. 优化代码性能

请提供完整、可运行的代码实现。
""",
        )

        reviewer_agent = create_agent(
            model=llm,
            tools=[search_tool],
            system_prompt="""
你是一个专业的代码审查员，擅长：
1. 检查代码质量
2. 识别潜在问题
3. 提供改进建议
4. 评估代码性能

请提供详细的审查报告。
""",
        )

        print("✓ 专业 Agent 创建完成")

        print("\n=== 3. 创建 Supervisor Agent ===")

        supervisor_agent = create_agent(
            model=llm,
            tools=[],
            system_prompt="""
你是 Supervisor Agent，负责协调多个专业 Agent 完成任务。

可用 Agent：
- Researcher: 负责信息搜集和研究
- Coder: 负责代码编写和调试
- Reviewer: 负责代码审查和质量检查

工作流程：
1. 分析用户任务类型
2. 分配给合适的 Agent
3. 协调多个 Agent 协作
4. 汇总最终结果

请根据任务需求，选择合适的 Agent 执行任务。
""",
        )

        print("✓ Supervisor Agent 创建完成")

        print("\n=== 4. 构建多 Agent 工作流 ===")

        def router(state: AgentState) -> str:
            """路由函数：决定下一个执行的 Agent"""
            last_message = state["messages"][-1]

            if "Researcher" in last_message.content:
                return "researcher"
            elif "Coder" in last_message.content:
                return "coder"
            elif "Reviewer" in last_message.content:
                return "reviewer"
            else:
                return END

        def supervisor_node(state: AgentState) -> AgentState:
            """Supervisor 节点"""
            messages = state["messages"]
            result = supervisor_agent.invoke({"messages": messages})
            return {
                "messages": [result["messages"][-1]],
                "next_agent": "researcher"
            }

        def researcher_node(state: AgentState) -> AgentState:
            """Researcher 节点"""
            messages = state["messages"]
            result = researcher_agent.invoke({"messages": messages})
            return {
                "messages": [result["messages"][-1]],
                "next_agent": "coder",
                "task_result": f"研究：{result['messages'][-1].content[:200]}..."
            }

        def coder_node(state: AgentState) -> AgentState:
            """Coder 节点"""
            messages = state["messages"]
            result = coder_agent.invoke({"messages": messages})
            return {
                "messages": [result["messages"][-1]],
                "next_agent": "reviewer",
                "task_result": f"代码：{result['messages'][-1].content[:200]}..."
            }

        def reviewer_node(state: AgentState) -> AgentState:
            """Reviewer 节点"""
            messages = state["messages"]
            result = reviewer_agent.invoke({"messages": messages})
            return {
                "messages": [result["messages"][-1]],
                "next_agent": END,
                "task_result": f"审查：{result['messages'][-1].content[:200]}..."
            }

        workflow = StateGraph(AgentState)

        workflow.add_node("supervisor", supervisor_node)
        workflow.add_node("researcher", researcher_node)
        workflow.add_node("coder", coder_node)
        workflow.add_node("reviewer", reviewer_node)

        workflow.set_entry_point("supervisor")

        workflow.add_conditional_edges(
            "supervisor",
            lambda state: state["next_agent"],
            {
                "researcher": "researcher",
                "coder": "coder",
                "reviewer": "reviewer",
                END: END,
            },
        )

        workflow.add_edge("researcher", "coder")
        workflow.add_edge("coder", "reviewer")
        workflow.add_edge("reviewer", END)

        checkpointer = InMemorySaver()
        app = workflow.compile(checkpointer=checkpointer)

        print("✓ 多 Agent 工作流构建完成")

        print("\n=== 5. 测试多 Agent 系统 ===")

        test_tasks = [
            "实现一个快速排序算法",
            "研究 Python 的最佳实践",
        ]

        for task in test_tasks:
            print(f"\n{'='*60}")
            print(f"🎯 用户请求：{task}")
            print(f"{'='*60}")

            config = {"configurable": {"thread_id": str(hash(task))}}

            initial_state: AgentState = {
                "messages": [{"role": "user", "content": task}],
                "next_agent": "supervisor",
                "task_result": "",
            }

            final_state = app.invoke(initial_state, config)

            print(f"\n📋 执行结果：")
            print(f"{'='*60}")
            print(final_state["task_result"])
            print(f"\n总消息数：{len(final_state['messages'])}")

            print(f"\n消息流转：")
            for i, msg in enumerate(final_state["messages"]):
                msg_type = type(msg).__name__
                content_preview = msg.content[:50] if hasattr(msg, 'content') else str(msg)[:50]
                print(f"{i+1}. {msg_type}: {content_preview}...")

        print("\n🎉 多智能体协作系统 (LangChain 1.0) 运行完成！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        print("\n请确保安装了 langgraph：")
        print("pip install langgraph")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

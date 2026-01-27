#!/usr/bin/env python3
"""
11 - 生产级追踪
使用 LangSmith 进行追踪、日志记录和性能监控，使用公共模块
"""

import os
import sys
import json
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv(override=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import PerformanceMonitor, CustomCallbackHandler, setup_langsmith


def example_simple_chain_with_tracing(monitor, callback):
    """示例 1: 简单 Chain 追踪"""
    print("\n" + "="*60)
    print("示例 1: 简单 Chain 追踪")
    print("="*60)

    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        from clients import create_model_client

        llm = create_model_client(temperature=0)
        prompt = ChatPromptTemplate.from_template("回答：{question}")

        chain = prompt | llm | StrOutputParser()

        monitor.start_tracking()

        response = chain.invoke(
            {"question": "什么是 LangChain？"},
            config={
                "tags": ["production", "simple"],
                "metadata": {"version": "1.0", "user_id": "demo"}
            }
        )

        metrics = monitor.end_tracking("simple_chain", True)
        print(f"响应: {response}")
        print(f"执行时间: {metrics.execution_time:.2f}秒")

    except Exception as e:
        metrics = monitor.end_tracking("simple_chain", False, str(e))
        print(f"错误: {e}")


def example_agent_with_tracing(monitor, callback):
    """示例 2: Agent 追踪"""
    print("\n" + "="*60)
    print("示例 2: Agent 追踪")
    print("="*60)

    monitor.start_tracking()

    try:
        from langchain.tools import tool
        from langchain.agents import AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        from clients import create_model_client

        llm = create_model_client(temperature=0)

        @tool
        def calculator(expression: str) -> str:
            """计算数学表达式"""
            try:
                result = eval(expression)
                return f"计算结果: {result}"
            except:
                return "计算错误"

        tools = [calculator]

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个智能助手，可以使用计算器工具。"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=False,
            max_iterations=3
        )

        response = agent_executor.invoke(
            {"input": "计算 25 * 4 + 18 等于多少？"},
            config={
                "tags": ["production", "agent"],
                "metadata": {"version": "1.0", "agent_type": "calculator"}
            }
        )

        metrics = monitor.end_tracking("agent_chain", True)
        print(f"响应: {response['output']}")
        print(f"执行时间: {metrics.execution_time:.2f}秒")

    except Exception as e:
        metrics = monitor.end_tracking("agent_chain", False, str(e))
        print(f"错误: {e}")


def example_rag_with_tracing(monitor, callback):
    """示例 3: RAG 追踪"""
    print("\n" + "="*60)
    print("示例 3: RAG 追踪")
    print("="*60)

    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_community.embeddings import FakeEmbeddings
        from langchain_community.vectorstores import Chroma

        from clients import create_model_client

        llm = create_model_client(temperature=0)

        documents = [
            "LangChain 是一个用于构建 LLM 应用的框架。",
            "LangChain 提供了链式调用、提示词管理等功能。",
            "LangChain 支持多种 LLM 提供商和工具。",
        ]

        print("⚠️  使用 FakeEmbeddings（仅用于演示）")
        embeddings = FakeEmbeddings(size=1536)
        vectorstore = Chroma.from_texts(documents, embeddings)
        retriever = vectorstore.as_retriever()

        prompt = ChatPromptTemplate.from_template("""
        基于以下上下文回答问题：

        上下文：{context}

        问题：{question}

        回答：
        """
        )

        chain = (
            {"context": retriever, "question": lambda x: x["question"]}
            | prompt
            | llm
            | StrOutputParser()
        )

        monitor.start_tracking()

        response = chain.invoke(
            {"question": "LangChain 有什么功能？"},
            config={
                "tags": ["production", "rag"],
                "metadata": {"version": "1.0", "retriever_type": "chroma"}
            }
        )

        metrics = monitor.end_tracking("rag_chain", True)
        print(f"响应: {response}")
        print(f"执行时间: {metrics.execution_time:.2f}秒")

    except Exception as e:
        metrics = monitor.end_tracking("rag_chain", False, str(e))
        print(f"错误: {e}")


def example_performance_comparison(monitor):
    """示例 4: 性能对比"""
    print("\n" + "="*60)
    print("示例 4: 性能对比")
    print("="*60)

    try:
        from clients import create_model_client

        test_question = "什么是人工智能？"

        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

        print(f"\n测试模型: {model_name}")

        try:
            llm = create_model_client(temperature=0)

            monitor.start_tracking()

            response = llm.invoke(test_question)

            metrics = monitor.end_tracking(f"model_{model_name}", True)
            print(f"响应长度: {len(response.content)} 字符")
            print(f"执行时间: {metrics.execution_time:.2f}秒")

        except Exception as e:
            metrics = monitor.end_tracking(f"model_{model_name}", False, str(e))
            print(f"错误: {e}")

    except Exception as e:
        print(f"性能对比错误: {e}")


def main():
    """主函数"""
    print("🦜🔗 11 - 生产级追踪")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    langsmith_enabled = setup_langsmith()

    monitor = PerformanceMonitor()
    callback = CustomCallbackHandler()

    try:
        example_simple_chain_with_tracing(monitor, callback)
        example_agent_with_tracing(monitor, callback)
        example_rag_with_tracing(monitor, callback)
        example_performance_comparison(monitor)

        print("\n" + "="*60)
        print("性能摘要")
        print("="*60)

        summary = monitor.get_summary()
        print(json.dumps(summary, indent=2, ensure_ascii=False))

        monitor.save_metrics()
        callback.save_logs()

        if langsmith_enabled:
            print("\n✓ 访问 LangSmith 查看详细追踪:")
            print("  https://smith.langchain.com/")

        print("\n🎉 生产级追踪示例运行完成！")

    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

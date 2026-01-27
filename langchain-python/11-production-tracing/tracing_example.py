#!/usr/bin/env python3
"""
11 - 生产级追踪
使用 LangSmith 进行追踪、日志记录和性能监控
"""

import os
import time
import json
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    chain_name: str
    execution_time: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    success: bool
    error_message: str = ""


class ProductionMonitor:
    """生产环境监控器"""

    def __init__(self):
        self.metrics_history = []
        self.start_time = None

    def start_tracking(self):
        """开始追踪"""
        self.start_time = time.time()

    def end_tracking(self, chain_name: str, success: bool, error: str = "") -> PerformanceMetrics:
        """结束追踪并记录指标"""
        if not self.start_time:
            raise ValueError("必须先调用 start_tracking()")

        execution_time = time.time() - self.start_time

        metrics = PerformanceMetrics(
            chain_name=chain_name,
            execution_time=execution_time,
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            success=success,
            error_message=error
        )

        self.metrics_history.append(metrics)
        self.start_time = None

        return metrics

    def get_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {"message": "没有记录的指标"}

        total_runs = len(self.metrics_history)
        successful_runs = sum(1 for m in self.metrics_history if m.success)
        failed_runs = total_runs - successful_runs

        avg_time = sum(m.execution_time for m in self.metrics_history) / total_runs
        total_tokens = sum(m.total_tokens for m in self.metrics_history)

        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": successful_runs / total_runs if total_runs > 0 else 0,
            "average_time": avg_time,
            "total_tokens": total_tokens,
            "estimated_cost": total_tokens * 0.00002,
        }

    def save_metrics(self, filename: str = "performance_metrics.json"):
        """保存指标到文件"""
        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "metrics": [asdict(m) for m in self.metrics_history]
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 指标已保存到 {filename}")


class CustomCallbackHandler:
    """自定义回调处理器"""

    def __init__(self):
        self.logs = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        """LLM 调用开始"""
        self.log("INFO", f"LLM 调用开始: {prompts[0][:50]}...")

    def on_llm_end(self, response, **kwargs):
        """LLM 调用结束"""
        self.log("INFO", "LLM 调用完成")

    def on_llm_error(self, error, **kwargs):
        """LLM 调用错误"""
        self.log("ERROR", f"LLM 错误: {error}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        """Chain 调用开始"""
        chain_name = serialized.get("name", "unknown")
        self.log("INFO", f"Chain '{chain_name}' 开始执行")

    def on_chain_end(self, outputs, **kwargs):
        """Chain 调用结束"""
        self.log("INFO", "Chain 执行完成")

    def on_chain_error(self, error, **kwargs):
        """Chain 调用错误"""
        self.log("ERROR", f"Chain 错误: {error}")

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Tool 调用开始"""
        tool_name = serialized.get("name", "unknown")
        self.log("INFO", f"Tool '{tool_name}' 开始执行: {input_str[:30]}...")

    def on_tool_end(self, output, **kwargs):
        """Tool 调用结束"""
        self.log("INFO", f"Tool 执行完成: {output[:50]}...")

    def on_tool_error(self, error, **kwargs):
        """Tool 调用错误"""
        self.log("ERROR", f"Tool 错误: {error}")

    def log(self, level: str, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def save_logs(self, filename: str = "reports/execution_logs.txt"):
        """保存日志到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs))

        print(f"✓ 日志已保存到 {filename}")


def setup_langsmith():
    """配置 LangSmith 追踪"""
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️  未设置 LANGSMITH_API_KEY，LangSmith 追踪已禁用")
        print("   访问 https://smith.langchain.com/ 获取 API Key")
        return False

    project_name = os.getenv("LANGSMITH_PROJECT", "agents-handbook")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_PROJECT"] = project_name

    print("✓ LangSmith 追踪已启用")
    print(f"  项目名称: {project_name}")
    print(f"  追踪地址: https://smith.langchain.com/")
    return True


def example_simple_chain_with_tracing(monitor, callback, openai_api_key, openai_base_url, model_name):
    """示例 1: 简单 Chain 追踪"""
    print("\n" + "="*60)
    print("示例 1: 简单 Chain 追踪")
    print("="*60)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )
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


def example_agent_with_tracing(monitor, callback, openai_api_key, openai_base_url, model_name):
    """示例 2: Agent 追踪"""
    print("\n" + "="*60)
    print("示例 2: Agent 追踪")
    print("="*60)

    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import tool, AgentExecutor, create_tool_calling_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )

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
            verbose=True,
            max_iterations=3
        )

        monitor.start_tracking()

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


def example_rag_with_tracing(monitor, callback, openai_api_key, openai_base_url, model_name):
    """示例 3: RAG 追踪"""
    print("\n" + "="*60)
    print("示例 3: RAG 追踪")
    print("="*60)

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_community.embeddings import FakeEmbeddings
        from langchain_community.vectorstores import Chroma

        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )

        documents = [
            "LangChain 是一个用于构建 LLM 应用的框架。",
            "LangChain 提供了链式调用、提示词管理等功能。",
            "LangChain 支持多种 LLM 提供商和工具。",
        ]

        embeddings = FakeEmbeddings(size=1536)
        vectorstore = Chroma.from_texts(documents, embeddings)
        retriever = vectorstore.as_retriever()

        prompt = ChatPromptTemplate.from_template("""
        基于以下上下文回答问题：

        上下文：{context}

        问题：{question}

        回答：
        """)

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


def example_performance_comparison(monitor, openai_api_key, openai_base_url, model_name):
    """示例 4: 性能对比"""
    print("\n" + "="*60)
    print("示例 4: 性能对比")
    print("="*60)

    try:
        from langchain_openai import ChatOpenAI

        test_question = "什么是人工智能？"

        models = [model_name]

        for model in models:
            print(f"\n测试模型: {model}")

            try:
                llm = ChatOpenAI(
                    model=model,
                    temperature=0,
                    api_key=SecretStr(openai_api_key),
                    base_url=openai_base_url
                )

                monitor.start_tracking()

                response = llm.invoke(test_question)

                metrics = monitor.end_tracking(f"model_{model}", True)
                print(f"响应长度: {len(response.content)} 字符")
                print(f"执行时间: {metrics.execution_time:.2f}秒")

            except Exception as e:
                metrics = monitor.end_tracking(f"model_{model}", False, str(e))
                print(f"错误: {e}")

    except Exception as e:
        print(f"性能对比错误: {e}")


def main():
    """主函数"""
    print("🦜🔗 11 - 生产级追踪")
    print("=" * 60)

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    if not openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    langsmith_enabled = setup_langsmith()

    monitor = ProductionMonitor()
    callback = CustomCallbackHandler()

    try:
        example_simple_chain_with_tracing(monitor, callback, openai_api_key, openai_base_url, model_name)
        example_agent_with_tracing(monitor, callback, openai_api_key, openai_base_url, model_name)
        example_rag_with_tracing(monitor, callback, openai_api_key, openai_base_url, model_name)
        example_performance_comparison(monitor, openai_api_key, openai_base_url, model_name)

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

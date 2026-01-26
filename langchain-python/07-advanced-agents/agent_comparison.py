#!/usr/bin/env python3
"""
Agent性能对比分析工具
比较不同Agent类型的性能表现
"""

import time
import json
import statistics
from typing import Dict, List, Any
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import SecretStr
import os

# 加载环境变量
load_dotenv(override=True)


@dataclass
class AgentMetrics:
    """Agent性能指标"""

    name: str
    response_time: float
    success_rate: float
    token_usage: int
    tool_calls: int
    reasoning_steps: int
    accuracy_score: float


class AgentComparator:
    """Agent性能对比器"""

    def __init__(self):
        self.test_questions = [
            {
                "question": "什么是Python？",
                "expected_keywords": ["编程语言", "高级语言", "解释型"],
                "difficulty": "简单",
            },
            {
                "question": "计算 15 * 8 + 32 等于多少？",
                "expected_answer": "152",
                "difficulty": "简单",
            },
            {
                "question": "LangChain的主要功能有哪些？请详细说明。",
                "expected_keywords": ["LLM", "提示词", "链", "智能体"],
                "difficulty": "中等",
            },
            {
                "question": "分析机器学习和深度学习的区别，并给出应用场景。",
                "expected_keywords": ["神经网络", "数据量", "复杂度", "应用"],
                "difficulty": "困难",
            },
        ]

        self.results = []

    def evaluate_response(self, question: Dict, response: str) -> float:
        """评估回答准确性"""
        score = 0.0

        # 检查期望关键词
        if "expected_keywords" in question:
            keyword_count = sum(
                1
                for keyword in question["expected_keywords"]
                if keyword.lower() in response.lower()
            )
            score += (keyword_count / len(question["expected_keywords"])) * 0.6

        # 检查期望答案
        if "expected_answer" in question:
            if question["expected_answer"] in response:
                score += 0.8

        # 检查回答质量
        if len(response) > 50:
            score += 0.2  # 内容充足
        if "。" in response or "." in response:
            score += 0.1  # 有完整句子

        return min(score, 1.0)

    def test_agent(self, agent, agent_name: str) -> AgentMetrics:
        """测试单个Agent"""
        print(f"\n=== 测试 {agent_name} ===")

        response_times = []
        success_count = 0
        token_usages = []
        tool_calls_list = []
        reasoning_steps_list = []
        accuracy_scores = []

        for i, question in enumerate(self.test_questions):
            print(f"问题 {i + 1}: {question['question']}")

            try:
                start_time = time.time()
                response = agent.invoke({"input": question["question"]})
                end_time = time.time()

                response_time = end_time - start_time
                response_times.append(response_time)

                # 评估回答
                answer = response.get("output", "")
                accuracy = self.evaluate_response(question, answer)
                accuracy_scores.append(accuracy)

                success_count += 1

                # 模拟其他指标（实际应用中需要从Agent执行中获取）
                token_usages.append(len(answer.split()) * 2)  # 估算token使用
                tool_calls_list.append(2)  # 假设平均2次工具调用
                reasoning_steps_list.append(3)  # 假设平均3个推理步骤

                print(f"回答：{answer[:100]}...")
                print(f"准确性：{accuracy:.2f}")
                print(f"响应时间：{response_time:.2f}秒")

            except Exception as e:
                print(f"错误：{e}")
                response_times.append(0)
                accuracy_scores.append(0)
                token_usages.append(0)
                tool_calls_list.append(0)
                reasoning_steps_list.append(0)

        # 计算平均指标
        metrics = AgentMetrics(
            name=agent_name,
            response_time=statistics.mean(response_times),
            success_rate=success_count / len(self.test_questions),
            token_usage=statistics.mean(token_usages),
            tool_calls=statistics.mean(tool_calls_list),
            reasoning_steps=statistics.mean(reasoning_steps_list),
            accuracy_score=statistics.mean(accuracy_scores),
        )

        self.results.append(metrics)
        return metrics

    def generate_comparison_report(self) -> str:
        """生成对比报告"""
        if not self.results:
            return "没有测试结果"

        report = []
        report.append("=" * 60)
        report.append("Agent性能对比报告")
        report.append("=" * 60)
        report.append("")

        # 详细指标表格
        report.append("详细性能指标：")
        report.append("-" * 60)
        report.append(
            f"{'Agent名称':<15} {'响应时间(s)':<10} {'成功率':<8} {'Token数':<8} {'工具调用':<8} {'推理步骤':<8} {'准确性':<8}"
        )
        report.append("-" * 60)

        for metrics in self.results:
            report.append(
                f"{metrics.name:<15} "
                f"{metrics.response_time:<10.2f} "
                f"{metrics.success_rate:<8.2%} "
                f"{metrics.token_usage:<8.0f} "
                f"{metrics.tool_calls:<8.1f} "
                f"{metrics.reasoning_steps:<8.1f} "
                f"{metrics.accuracy_score:<8.2%}"
            )

        report.append("")

        # 性能排名
        report.append("性能排名：")
        report.append("-" * 30)

        rankings = {
            "响应速度": sorted(self.results, key=lambda x: x.response_time),
            "准确性": sorted(
                self.results, key=lambda x: x.accuracy_score, reverse=True
            ),
            "成功率": sorted(self.results, key=lambda x: x.success_rate, reverse=True),
            "效率": sorted(
                self.results, key=lambda x: x.token_usage / (x.accuracy_score + 0.01)
            ),
        }

        for metric_name, ranking in rankings.items():
            report.append(f"\n{metric_name}排名：")
            for i, metrics in enumerate(ranking, 1):
                report.append(f"  {i}. {metrics.name}")

        # 推荐建议
        report.append("\n" + "=" * 30)
        report.append("推荐建议：")
        report.append("-" * 30)

        best_accuracy = max(self.results, key=lambda x: x.accuracy_score)
        fastest = min(self.results, key=lambda x: x.response_time)
        most_reliable = max(self.results, key=lambda x: x.success_rate)

        report.append(
            f"• 最高准确性：{best_accuracy.name} (准确性: {best_accuracy.accuracy_score:.2%})"
        )
        report.append(
            f"• 最快响应：{fastest.name} (响应时间: {fastest.response_time:.2f}s)"
        )
        report.append(
            f"• 最可靠：{most_reliable.name} (成功率: {most_reliable.success_rate:.2%})"
        )

        # 使用场景建议
        report.append("\n使用场景建议：")
        report.append("-" * 20)

        for metrics in self.results:
            if metrics.accuracy_score > 0.8:
                scenario = "高质量问答、知识检索"
            elif metrics.response_time < 2.0:
                scenario = "实时对话、快速响应"
            elif metrics.success_rate > 0.9:
                scenario = "生产环境、关键任务"
            else:
                scenario = "开发测试、实验性应用"

            report.append(f"• {metrics.name}: {scenario}")

        return "\n".join(report)

    def save_results(self, filename: str = "agent_comparison_results.json"):
        """保存结果到文件"""
        data = {
            "timestamp": time.time(),
            "test_questions": self.test_questions,
            "results": [
                {
                    "name": m.name,
                    "response_time": m.response_time,
                    "success_rate": m.success_rate,
                    "token_usage": m.token_usage,
                    "tool_calls": m.tool_calls,
                    "reasoning_steps": m.reasoning_steps,
                    "accuracy_score": m.accuracy_score,
                }
                for m in self.results
            ],
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"结果已保存到 {filename}")


def main():
    """主函数"""
    print("🔬 Agent性能对比分析工具")
    print("=" * 50)

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    # 检查环境
    if not openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        # 导入LangChain组件
        from langchain_openai import ChatOpenAI
        from langchain.agents import (
            tool,
            AgentExecutor,
            create_react_agent,
            create_tool_calling_agent,
        )
        from langchain_core.prompts import (
            PromptTemplate,
            ChatPromptTemplate,
            MessagesPlaceholder,
        )

        print("✓ 组件导入成功")

        # 初始化LLM
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )

        # 创建测试工具
        @tool
        def search_info(query: str) -> str:
            """搜索信息工具"""
            database = {
                "Python": "Python是一种高级编程语言，由Guido van Rossum创建，具有简洁的语法和强大的功能。",
                "LangChain": "LangChain是用于构建LLM应用的框架，提供了链式调用、提示词管理、智能体等功能。",
                "机器学习": "机器学习是人工智能的分支，让计算机能够从数据中学习模式和规律。",
                "深度学习": "深度学习使用神经网络模拟人脑，是机器学习的一个子领域。",
            }

            for key, value in database.items():
                if query.lower() in key.lower():
                    return value

            return f"未找到关于'{query}'的信息"

        @tool
        def calculate(expression: str) -> str:
            """数学计算工具"""
            try:
                # 安全的数学表达式计算
                allowed_chars = set("0123456789+-*/().")
                if all(c in allowed_chars for c in expression):
                    result = eval(expression)
                    return f"计算结果：{result}"
                else:
                    return "表达式包含不允许的字符"
            except:
                return "计算错误，请检查表达式"

        tools = [search_info, calculate]

        # 创建不同类型的Agent
        agents = {}

        # 1. ReAct Agent
        react_prompt = PromptTemplate.from_template("""
        回答问题，你可以使用这些工具：
        {tools}

        使用格式：
        Question: 问题
        Thought: 思考
        Action: 工具
        Action Input: 输入
        Observation: 结果
        ... (重复)
        Final Answer: 最终答案

        Question: {input}
        Thought: {agent_scratchpad}
        """)

        react_agent = create_react_agent(llm, tools, react_prompt)
        agents["ReAct"] = AgentExecutor(agent=react_agent, tools=tools, verbose=False)

        # 2. Tool Calling Agent
        functions_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个智能助手，可以使用工具获取信息并进行计算。"),
                ("user", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        functions_agent = create_tool_calling_agent(llm, tools, functions_prompt)
        agents["Tool Calling"] = AgentExecutor(
            agent=functions_agent, tools=tools, verbose=False
        )

        # 3. 简单Chain（作为对比基准）
        simple_prompt = PromptTemplate.from_template("请回答：{input}")
        simple_chain = simple_prompt | llm

        class SimpleAgentWrapper:
            def __init__(self, chain):
                self.chain = chain

            def invoke(self, input_data):
                result = self.chain.invoke(input_data["input"])
                return {"output": result.content}

        agents["Simple Chain"] = SimpleAgentWrapper(simple_chain)

        # 运行对比测试
        comparator = AgentComparator()

        for agent_name, agent in agents.items():
            comparator.test_agent(agent, agent_name)

        # 生成报告
        report = comparator.generate_comparison_report()
        print("\n" + report)

        # 保存结果
        comparator.save_results()

        print("\n🎉 性能对比分析完成！")

    except Exception as e:
        print(f"❌ 运行错误：{e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

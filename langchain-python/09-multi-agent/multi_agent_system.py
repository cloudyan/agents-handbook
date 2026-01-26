#!/usr/bin/env python3
"""
09 - 多智能体协作系统
Supervisor 模式：一个管理 Agent 协调多个专业 Agent
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


@dataclass
class AgentMessage:
    """Agent 通信消息"""
    sender: str
    receiver: str
    content: str
    context: Dict[str, Any]


class BaseAgent:
    """基础 Agent 类"""

    def __init__(self, name: str, role: str, llm, tools: List[Any] = None):
        self.name = name
        self.role = role
        self.llm = llm
        self.tools = tools or []
        self.message_history = []

    def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """接收并处理消息"""
        self.message_history.append(message)
        return self.process_message(message)

    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """处理消息，子类需要实现"""
        raise NotImplementedError

    def send_message(self, receiver: str, content: str, context: Dict[str, Any] = None) -> AgentMessage:
        """发送消息"""
        return AgentMessage(
            sender=self.name,
            receiver=receiver,
            content=content,
            context=context or {}
        )


class ResearcherAgent(BaseAgent):
    """研究 Agent：负责信息搜集和研究"""

    def __init__(self, llm, search_tool):
        super().__init__(
            name="Researcher",
            role="信息搜集和研究专家",
            llm=llm,
            tools=[search_tool]
        )
        self.system_prompt = """你是一个专业的研究助手，擅长：
1. 搜集和分析信息
2. 研究技术文档
3. 总结关键发现
4. 提供深入见解

请基于搜集的信息提供详细、准确的研究报告。"""

    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """处理研究任务"""
        task = message.content
        context = message.context

        print(f"\n[{self.name}] 接到任务：{task}")

        # 搜索相关信息
        search_query = f"{task} 技术细节"
        search_result = self.tools[0].invoke({"query": search_query})

        # 生成研究报告
        research_prompt = f"""{self.system_prompt}

任务：{task}
搜索结果：{search_result}

请提供详细的研究报告，包括：
1. 核心概念
2. 关键技术点
3. 最佳实践
4. 注意事项
"""

        response = self.llm.invoke(research_prompt)
        research_report = response.content

        print(f"[{self.name}] 研究完成")

        # 返回研究结果给发送者
        return self.send_message(
            receiver=message.sender,
            content=f"研究报告：\n{research_report}",
            context={"type": "research_result", "original_task": task}
        )


class CoderAgent(BaseAgent):
    """编码 Agent：负责代码编写和调试"""

    def __init__(self, llm):
        super().__init__(
            name="Coder",
            role="代码编写和调试专家",
            llm=llm
        )
        self.system_prompt = """你是一个专业的程序员，擅长：
1. 编写高质量的代码
2. 遵循最佳实践
3. 添加清晰的注释
4. 优化代码性能

请提供完整、可运行的代码实现。"""

    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """处理编码任务"""
        task = message.content
        context = message.context

        print(f"\n[{self.name}] 接到任务：{task}")

        # 如果有研究背景，结合研究内容
        research_context = context.get("research_result", "")
        if research_context:
            coding_prompt = f"""{self.system_prompt}

任务：{task}

研究背景：
{research_context}

请提供：
1. 完整的代码实现
2. 代码注释说明
3. 使用示例
"""
        else:
            coding_prompt = f"""{self.system_prompt}

任务：{task}

请提供：
1. 完整的代码实现
2. 代码注释说明
3. 使用示例
"""

        response = self.llm.invoke(coding_prompt)
        code_content = response.content

        print(f"[{self.name}] 代码编写完成")

        return self.send_message(
            receiver=message.sender,
            content=f"代码实现：\n{code_content}",
            context={"type": "code_result", "original_task": task}
        )


class ReviewerAgent(BaseAgent):
    """审查 Agent：负责代码审查和质量检查"""

    def __init__(self, llm):
        super().__init__(
            name="Reviewer",
            role="代码审查和质量检查专家",
            llm=llm
        )
        self.system_prompt = """你是一个专业的代码审查员，擅长：
1. 检查代码质量
2. 识别潜在问题
3. 提供改进建议
4. 评估代码性能

请提供详细的审查报告。"""

    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """处理审查任务"""
        task = message.content
        context = message.context

        print(f"\n[{self.name}] 接到任务：审查代码")

        # 提取代码内容
        code_content = context.get("code_result", task)

        # 生成审查报告
        review_prompt = f"""{self.system_prompt}

请审查以下代码：
{code_content}

审查要点：
1. 代码正确性
2. 代码风格
3. 性能优化
4. 错误处理
5. 最佳实践

请提供详细的审查报告和改进建议。
"""

        response = self.llm.invoke(review_prompt)
        review_report = response.content

        print(f"[{self.name}] 审查完成")

        return self.send_message(
            receiver=message.sender,
            content=f"审查报告：\n{review_report}",
            context={"type": "review_result", "original_task": task}
        )


class PlannerAgent(BaseAgent):
    """规划 Agent：负责任务规划和分解"""

    def __init__(self, llm):
        super().__init__(
            name="Planner",
            role="任务规划和分解专家",
            llm=llm
        )
        self.system_prompt = """你是一个专业的项目规划师，擅长：
1. 分析复杂任务
2. 分解任务步骤
3. 制定执行计划
4. 识别依赖关系

请提供清晰的执行计划。"""

    def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """处理规划任务"""
        task = message.content

        print(f"\n[{self.name}] 接到任务：规划任务")

        # 生成执行计划
        plan_prompt = f"""{self.system_prompt}

用户任务：{task}

请分析任务并制定执行计划：
1. 识别任务类型（代码开发、技术研究、问题解决等）
2. 分解任务步骤
3. 确定需要的 Agent 类型
4. 设置执行顺序

请以 JSON 格式返回计划：
{{
  "task_type": "类型",
  "steps": [
    {{"step": 1, "description": "步骤描述", "agent": "需要的Agent", "dependencies": []}}
  ]
}}
"""

        response = self.llm.invoke(plan_prompt)
        plan_content = response.content

        print(f"[{self.name}] 规划完成")

        return self.send_message(
            receiver=message.sender,
            content=f"执行计划：\n{plan_content}",
            context={"type": "plan_result", "original_task": task}
        )


class SupervisorAgent:
    """管理 Agent：协调多个专业 Agent"""

    def __init__(self, llm):
        self.name = "Supervisor"
        self.llm = llm
        self.agents: Dict[str, BaseAgent] = {}
        self.message_queue: List[AgentMessage] = []
        self.task_history = []

    def register_agent(self, agent: BaseAgent):
        """注册 Agent"""
        self.agents[agent.name] = agent
        print(f"✓ 注册 Agent: {agent.name} ({agent.role})")

    def coordinate_task(self, user_request: str) -> str:
        """协调执行用户任务"""
        print(f"\n{'='*60}")
        print(f"🎯 用户请求：{user_request}")
        print(f"{'='*60}")

        # 1. 使用 Planner 制定计划
        if "Planner" in self.agents:
            planner = self.agents["Planner"]
            plan_message = planner.send_message(
                receiver="Planner",
                content=user_request
            )
            plan_response = planner.receive_message(plan_message)

            if plan_response:
                print(f"\n[Supervisor] 收到计划：\n{plan_response.content[:200]}...")

        # 2. 根据任务类型分配 Agent
        task_type = self._analyze_task_type(user_request)

        if task_type == "code_development":
            return self._coordinate_code_development(user_request)
        elif task_type == "research":
            return self._coordinate_research(user_request)
        else:
            return self._coordinate_general_task(user_request)

    def _analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        code_keywords = ["实现", "编写", "代码", "函数", "算法", "程序"]
        research_keywords = ["研究", "分析", "比较", "调研", "技术"]

        task_lower = task.lower()

        if any(keyword in task_lower for keyword in code_keywords):
            return "code_development"
        elif any(keyword in task_lower for keyword in research_keywords):
            return "research"
        else:
            return "general"

    def _coordinate_code_development(self, task: str) -> str:
        """协调代码开发任务"""
        results = []

        # 步骤 1: 研究
        if "Researcher" in self.agents:
            researcher = self.agents["Researcher"]
            research_message = researcher.send_message(
                receiver="Researcher",
                content=f"研究如何{task}"
            )
            research_response = researcher.receive_message(research_message)
            if research_response:
                results.append(research_response.content)

        # 步骤 2: 编码
        if "Coder" in self.agents:
            coder = self.agents["Coder"]
            research_context = results[-1] if results else ""
            code_message = coder.send_message(
                receiver="Coder",
                content=f"实现{task}",
                context={"research_result": research_context}
            )
            code_response = coder.receive_message(code_message)
            if code_response:
                results.append(code_response.content)

        # 步骤 3: 审查
        if "Reviewer" in self.agents and len(results) >= 2:
            reviewer = self.agents["Reviewer"]
            review_message = reviewer.send_message(
                receiver="Reviewer",
                content="审查代码",
                context={"code_result": results[-1]}
            )
            review_response = reviewer.receive_message(review_message)
            if review_response:
                results.append(review_response.content)

        # 步骤 4: 汇总结果
        summary = self._summarize_results(task, results)
        return summary

    def _coordinate_research(self, task: str) -> str:
        """协调研究任务"""
        results = []

        if "Researcher" in self.agents:
            researcher = self.agents["Researcher"]
            research_message = researcher.send_message(
                receiver="Researcher",
                content=task
            )
            research_response = researcher.receive_message(research_message)
            if research_response:
                results.append(research_response.content)

        summary = self._summarize_results(task, results)
        return summary

    def _coordinate_general_task(self, task: str) -> str:
        """协调一般任务"""
        if "Researcher" in self.agents:
            researcher = self.agents["Researcher"]
            research_message = researcher.send_message(
                receiver="Researcher",
                content=task
            )
            research_response = researcher.receive_message(research_message)
            if research_response:
                return research_response.content

        return "任务完成"

    def _summarize_results(self, task: str, results: List[str]) -> str:
        """汇总结果"""
        print(f"\n[Supervisor] 汇总 {len(results)} 个结果")

        summary_prompt = f"""作为 Supervisor，请汇总以下任务执行结果：

用户任务：{task}

执行结果：
{chr(10).join(f'{i+1}. {result[:300]}...' for i, result in enumerate(results))}

请提供：
1. 任务完成情况
2. 关键成果
3. 建议
4. 下一步行动
"""

        response = self.llm.invoke(summary_prompt)
        return response.content


def main():
    print("🦜🔗 09 - 多智能体协作系统")
    print("=" * 60)

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    if not openai_api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        from langchain_openai import ChatOpenAI
        from langchain.agents import tool

        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )

        # 创建搜索工具
        @tool
        def search_tool(query: str) -> str:
            """搜索工具（模拟）"""
            knowledge_base = {
                "快速排序": "快速排序是一种分治算法，平均时间复杂度 O(n log n)，通过选择基准元素分区实现。",
                "Python": "Python 是一种高级编程语言，语法简洁，适合快速开发。",
                "算法": "算法是解决特定问题的一系列明确步骤。",
                "代码优化": "代码优化包括时间复杂度优化、空间复杂度优化、代码可读性提升等。",
            }

            for key, value in knowledge_base.items():
                if key in query:
                    return f"找到：{value}"

            return f"关于 '{query}' 的搜索结果：建议查阅官方文档和技术博客。"

        # 创建 Supervisor
        supervisor = SupervisorAgent(llm)

        # 注册子 Agent
        supervisor.register_agent(ResearcherAgent(llm, search_tool))
        supervisor.register_agent(CoderAgent(llm))
        supervisor.register_agent(ReviewerAgent(llm))
        supervisor.register_agent(PlannerAgent(llm))

        print("\n✓ 多智能体系统初始化完成\n")

        # 测试场景
        test_tasks = [
            "实现一个快速排序算法",
            "研究 Python 的最佳实践",
        ]

        for task in test_tasks:
            result = supervisor.coordinate_task(task)
            print(f"\n{'='*60}")
            print(f"📋 最终结果：")
            print(f"{'='*60}")
            print(result)
            print("\n")

        print("🎉 多智能体协作系统运行完成！")

    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

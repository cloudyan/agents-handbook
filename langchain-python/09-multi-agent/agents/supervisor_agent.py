"""监督 Agent - 任务协调和分配"""

from typing import Optional
from .base_agent import BaseAgent, AgentMessage


class SupervisorAgent:
    """监督 Agent，负责协调多个专业 Agent"""
    
    def __init__(self, llm):
        self.name = "Supervisor"
        self.llm = llm
        self.agents: dict[str, BaseAgent] = {}
    
    def register_agent(self, agent: BaseAgent) -> None:
        """注册 Agent"""
        self.agents[agent.name] = agent
        print(f"✓ 注册 Agent: {agent.name} ({agent.role})")
    
    async def coordinate_task(self, user_request: str) -> str:
        """协调任务执行"""
        print(f"\n{'='*60}")
        print(f"🎯 用户请求：{user_request}")
        print("="*60)
        
        task_type = self.analyze_task_type(user_request)
        
        if task_type == "code_development":
            return await self.coordinate_code_development(user_request)
        elif task_type == "research":
            return await self.coordinate_research(user_request)
        else:
            return await self.coordinate_general_task(user_request)
    
    def analyze_task_type(self, task: str) -> str:
        """分析任务类型"""
        code_keywords = ["实现", "编写", "代码", "函数", "算法", "程序"]
        research_keywords = ["研究", "分析", "比较", "调研", "技术"]
        
        task_lower = task.lower()
        
        if any(kw in task_lower for kw in code_keywords):
            return "code_development"
        elif any(kw in task_lower for kw in research_keywords):
            return "research"
        else:
            return "general"
    
    async def coordinate_code_development(self, task: str) -> str:
        """协调代码开发任务"""
        results = []
        
        research_report = ""
        if "Researcher" in self.agents:
            researcher = self.agents["Researcher"]
            research_message = researcher.send_message("Supervisor", f"研究如何{task}")
            research_response = await researcher.receive_message(research_message)
            if research_response:
                research_report = research_response.content
                results.append(research_report)
                print(f"\n[Supervisor] 收到研究报告")
        
        code_content = ""
        if "Coder" in self.agents:
            coder = self.agents["Coder"]
            code_task = f"根据以下研究报告编写代码：\n\n{research_report}\n\n任务：{task}" if research_report else task
            code_message = coder.send_message("Supervisor", code_task)
            code_response = await coder.receive_message(code_message)
            if code_response:
                code_content = code_response.content
                results.append(code_content)
                print(f"\n[Supervisor] 收到代码实现 ({len(code_content)} 字符)")
        
        if "Reviewer" in self.agents and code_content:
            reviewer = self.agents["Reviewer"]
            review_message = reviewer.send_message("Supervisor", code_content)
            review_response = await reviewer.receive_message(review_message)
            if review_response:
                results.append(review_response.content)
                print(f"\n[Supervisor] 收到审查报告")
        
        summary = await self.summarize_results(task, results)
        return summary
    
    async def coordinate_research(self, task: str) -> str:
        """协调研究任务"""
        results = []
        
        if "Researcher" in self.agents:
            researcher = self.agents["Researcher"]
            research_message = researcher.send_message("Supervisor", task)
            research_response = await researcher.receive_message(research_message)
            if research_response:
                results.append(research_response.content)
                print(f"\n[Supervisor] 收到研究结果")
        
        summary = await self.summarize_results(task, results)
        return summary
    
    async def coordinate_general_task(self, task: str) -> str:
        """协调通用任务"""
        if "Researcher" in self.agents:
            researcher = self.agents["Researcher"]
            research_message = researcher.send_message("Supervisor", task)
            research_response = await researcher.receive_message(research_message)
            if research_response:
                print(f"\n[Supervisor] 收到研究结果")
                return research_response.content
        
        return "任务完成"
    
    async def summarize_results(self, task: str, results: list[str]) -> str:
        """汇总结果"""
        print(f"\n[Supervisor] 汇总 {len(results)} 个结果")
        
        summary_prompt = f"""作为 Supervisor，请汇总以下任务执行结果：

用户任务：{task}

执行结果：
{chr(10).join([f"{i+1}. {r[:300]}..." for i, r in enumerate(results)])}

请提供：
1. 任务完成情况
2. 关键成果
3. 建议
4. 下一步行动"""
        
        response = await self.llm.ainvoke(summary_prompt)
        return response.content

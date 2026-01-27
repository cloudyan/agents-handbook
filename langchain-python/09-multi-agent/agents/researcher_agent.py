"""研究员 Agent - 信息搜集和研究"""

from .base_agent import BaseAgent, AgentMessage


class ResearcherAgent(BaseAgent):
    """研究员 Agent，擅长信息搜集和研究"""
    
    def __init__(self, llm, search_tool):
        super().__init__("Researcher", "信息搜集和研究专家", llm, [search_tool])
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """处理消息"""
        task = message.content
        
        print(f"\n[{self.name}] 接到任务：{task}")
        
        search_result = await self.tools[0].ainvoke({"query": f"{task} 技术细节"})
        
        research_prompt = f"""你是一个专业的研究助手，擅长：
1. 搜集和分析信息
2. 研究技术文档
3. 总结关键发现
4. 提供深入见解

任务：{task}
搜索结果：{search_result}

请提供详细的研究报告，包括：
1. 核心概念
2. 关键技术点
3. 最佳实践
4. 注意事项"""
        
        response = await self.llm.ainvoke(research_prompt)
        research_report = response.content
        
        print(f"[{self.name}] 研究完成")
        print(f"\n{'─'*60}")
        print(f"📚 [{self.name}] 研究报告：")
        print("─"*60)
        print(research_report)
        print("─"*60)
        print("\n"*3)
        
        return self.send_message(
            message.sender,
            f"研究报告：\n{research_report}"
        )

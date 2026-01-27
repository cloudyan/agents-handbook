"""审查 Agent - 代码审查"""

from .base_agent import BaseAgent, AgentMessage


class ReviewerAgent(BaseAgent):
    """审查 Agent，擅长代码审查"""
    
    def __init__(self, llm):
        super().__init__("Reviewer", "专业代码审查员", llm, [])
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """处理消息"""
        code_content = message.content
        
        print(f"\n[{self.name}] 接到审查任务")
        
        review_prompt = f"""你是一个专业的代码审查员，擅长：
1. 检查代码质量
2. 识别潜在问题
3. 提供改进建议
4. 评估代码性能

代码内容：
{code_content}

请提供详细的审查报告，包括：
1. 代码质量评估
2. 发现的问题
3. 改进建议
4. 性能优化建议"""
        
        response = await self.llm.ainvoke(review_prompt)
        review_report = response.content
        
        print(f"[{self.name}] 审查完成")
        print(f"\n{'─'*60}")
        print(f"🔍 [{self.name}] 审查报告：")
        print("─"*60)
        print(review_report[:500] + "..." if len(review_report) > 500 else review_report)
        print("─"*60)
        print("\n"*3)
        
        return self.send_message(
            message.sender,
            review_report
        )

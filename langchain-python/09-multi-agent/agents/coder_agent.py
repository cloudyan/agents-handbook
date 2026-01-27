"""编码 Agent - 代码实现"""

from .base_agent import BaseAgent, AgentMessage


class CoderAgent(BaseAgent):
    """编码 Agent，擅长代码编写"""
    
    def __init__(self, llm):
        super().__init__("Coder", "专业程序员", llm, [])
    
    async def process_message(self, message: AgentMessage) -> AgentMessage:
        """处理消息"""
        task = message.content
        
        print(f"\n[{self.name}] 接到任务：{task[:50]}...")
        
        coding_prompt = f"""你是一个专业的程序员，擅长：
1. 编写高质量的代码
2. 遵循最佳实践
3. 添加清晰的注释
4. 优化代码性能

任务：{task}

请提供完整、可运行的代码实现，包括：
1. 代码实现
2. 关键注释
3. 使用说明
4. 测试示例"""
        
        response = await self.llm.ainvoke(coding_prompt)
        code_content = response.content
        
        print(f"[{self.name}] 代码实现完成 ({len(code_content)} 字符)")
        print(f"\n{'─'*60}")
        print(f"💻 [{self.name}] 代码实现：")
        print("─"*60)
        print(code_content[:500] + "..." if len(code_content) > 500 else code_content)
        print("─"*60)
        print("\n"*3)
        
        return self.send_message(
            message.sender,
            code_content
        )

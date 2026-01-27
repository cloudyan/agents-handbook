"""基础 Agent 类"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AgentMessage:
    """Agent 消息"""
    sender: str
    receiver: str
    content: str


class BaseAgent:
    """基础 Agent 类"""
    
    def __init__(self, name: str, role: str, llm, tools: list = None):
        self.name = name
        self.role = role
        self.llm = llm
        self.tools = tools or []
        self.message_history: list[AgentMessage] = []
    
    async def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """接收消息"""
        self.message_history.append(message)
        return await self.process_message(message)
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """处理消息（子类必须实现）"""
        raise NotImplementedError("子类必须实现 process_message 方法")
    
    def send_message(self, receiver: str, content: str) -> AgentMessage:
        """发送消息"""
        return AgentMessage(
            sender=self.name,
            receiver=receiver,
            content=content
        )

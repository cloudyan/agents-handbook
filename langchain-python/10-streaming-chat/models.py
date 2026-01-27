"""
数据模型定义
使用 Pydantic 提供类型安全和数据验证
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Message(BaseModel):
    """消息模型"""
    role: str = Field(..., description="消息角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class ChatSessionState(BaseModel):
    """聊天会话状态"""
    message_history: List[Message] = Field(default_factory=list, description="消息历史记录")

    def add_user_message(self, content: str) -> None:
        """添加用户消息"""
        self.message_history.append(Message(role="user", content=content))

    def add_assistant_message(self, content: str) -> None:
        """添加助手消息"""
        self.message_history.append(Message(role="assistant", content=content))

    def get_messages_for_llm(self, current_message: str) -> List[dict]:
        """获取用于 LLM 的消息列表"""
        messages = []
        for msg in self.message_history:
            messages.append({"role": msg.role, "content": msg.content})
        messages.append({"role": "user", "content": current_message})
        return messages


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(default="ok", description="服务状态")
    active_sessions: int = Field(default=0, description="活跃会话数")
    timestamp: Optional[str] = Field(default=None, description="时间戳")

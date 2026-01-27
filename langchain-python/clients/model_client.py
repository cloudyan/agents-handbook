"""模型客户端模块"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import ChatOpenAI

load_dotenv(override=True)


def create_model_client(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    streaming: bool = False,
) -> ChatOpenAI:
    """创建 OpenAI 模型客户端

    Args:
        model_name: 模型名称，默认从环境变量读取
        temperature: 温度参数，默认 0.7
        streaming: 是否启用流式输出，默认 False

    Returns:
        ChatOpenAI 实例
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置 OPENAI_API_KEY 环境变量")

    base_url = os.getenv("OPENAI_BASE_URL")
    model = model_name or os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    # 确保 model 和 base_url 不是 None
    final_model = model if model else "gpt-3.5-turbo"
    final_base_url = base_url if base_url else "https://api.openai.com/v1"

    return ChatOpenAI(
        model=final_model,
        api_key=SecretStr(api_key),
        base_url=final_base_url,
        temperature=temperature,
        streaming=streaming,
    )

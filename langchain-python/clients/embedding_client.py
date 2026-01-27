"""嵌入客户端模块"""
import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import FakeEmbeddings
from langchain_ollama import OllamaEmbeddings

load_dotenv(override=True)


def create_embedding_client(
    model_name: Optional[str] = None,
    use_fake: bool = False,
    use_ollama: bool = False,
):
    """创建嵌入客户端

    Args:
        model_name: 嵌入模型名称，默认从环境变量读取
        use_fake: 是否使用 FakeEmbeddings（用于不支持 embeddings 的 API）
        use_ollama: 是否使用 Ollama 嵌入

    Returns:
        嵌入客户端实例
    """
    if use_fake:
        print("⚠️  使用 FakeEmbeddings（仅用于演示，不支持实际向量检索）")
        return FakeEmbeddings(size=1536)

    if use_ollama:
        print("✓ 使用 Ollama 嵌入")
        ollama_model = model_name or "nomic-embed-text"
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        return OllamaEmbeddings(
            model=ollama_model,
            base_url=ollama_url if ollama_url else "http://localhost:11434",
        )

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("请设置 OPENAI_API_KEY 环境变量")

    base_url = os.getenv("OPENAI_BASE_URL")
    model = model_name or os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-ada-002")
    
    # 确保 model 和 base_url 不是 None
    final_model = model if model else "text-embedding-ada-002"
    final_base_url = base_url if base_url else "https://api.openai.com/v1"

    try:
        return OpenAIEmbeddings(
            model=final_model,
            api_key=SecretStr(api_key),
            base_url=final_base_url,
        )
    except Exception as e:
        print(f"⚠️  创建 OpenAIEmbeddings 失败: {e}")
        print("⚠️  使用 FakeEmbeddings 作为替代")
        return FakeEmbeddings(size=1536)

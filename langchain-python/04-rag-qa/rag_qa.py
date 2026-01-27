#!/usr/bin/env python3
"""
04 - RAG QA (LCEL 版本)
学习检索增强生成（RAG）技术，通过文档检索来提高问答的准确性

参考 TypeScript 版本实现，使用 Ollama 做嵌入，Chroma 做向量存储
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)


def main():
    print("🦜🔗 04 - RAG QA (LCEL)")
    print("=" * 40)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        import requests
        from bs4 import BeautifulSoup
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_chroma import Chroma
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from clients import create_model_client, create_embedding_client

        print("✓ LangChain 组件导入完成")

        print("\n=== 1. 准备文档数据 ===")

        url = "https://docs.langchain.com/oss/python/langchain/overview"
        print(f"正在获取文档: {url}")

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            print(f"✓ 成功获取文档 (状态码: {response.status_code})")

            soup = BeautifulSoup(response.content, 'html.parser')

            body_text = soup.body.get_text(separator='\n', strip=True)

            print(f"✓ 文档解析完成")
            print(f"文档长度: {len(body_text)} 字符")

        except requests.RequestException as e:
            print(f"⚠️  获取文档失败: {e}")
            print("使用备用文档内容...")

            body_text = """
            LangChain 是一个用于构建基于大语言模型应用程序的框架。
            它提供了一套工具和组件，帮助开发者更容易地创建复杂的 AI 应用。

            LangChain 的核心功能包括：
            - 模型抽象：统一不同 LLM 提供商的接口
            - 提示词管理：创建和管理复杂的提示词模板
            - 链式调用：将多个组件串联成工作流
            - 记忆管理：为对话系统添加记忆功能
            - 智能体：创建能够使用工具的自主智能体
            - 索引和检索：构建 RAG 系统

            LangChain 支持多种 LLM 提供商，包括 OpenAI、Anthropic、Hugging Face 等。
            它还提供了丰富的集成，如向量数据库、文档加载器、工具等。
            """

        print("\n=== 2. 分割文档 ===")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

        chunks = text_splitter.split_text(body_text)
        print(f"✓ 文档分割完成，共 {len(chunks)} 个片段")

        print("\n=== 3. 创建向量索引 ===")

        print("使用 Ollama 嵌入模型...")
        embeddings = create_embedding_client(use_ollama=True)

        print("连接到 Chroma 服务 (Docker)...")
        vector_store = Chroma.from_texts(
            texts=chunks,
            embedding=embeddings,
            metadatas=[{"source": "langchain-docs", "index": i} for i in range(len(chunks))],
            collection_name="rag-qa-demo",
            persist_directory=None,
        )
        print("✓ 向量索引创建完成")

        print("\n=== 4. 初始化问答系统 ===")

        llm = create_model_client(temperature=0)

        prompt = ChatPromptTemplate.from_template("""
请根据以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法回答。

上下文:
{context}

问题: {input}

回答:
""")

        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        def format_docs(docs):
            """格式化检索到的文档"""
            return "\n\n".join(doc.page_content for doc in docs)

        rag_chain = (
            {"context": retriever | format_docs, "input": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        print("✓ RAG 问答系统初始化完成")

        print("\n=== 5. 测试问答 ===")

        test_questions = [
            "关于 LangChain 你知道什么？",
            "LangChain 提供哪些核心功能？",
            "什么是机器学习？",
        ]

        for question in test_questions:
            print(f"\n问题: {question}")
            print("-" * 50)

            result = rag_chain.invoke(question)

            print(f"回答: {result}")

        print("\n" + "=" * 50)
        print("RAG 问答系统运行完成！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        print("\n请确保安装了以下依赖：")
        print("  pip install requests beautifulsoup4 langchain-text-splitters langchain-chroma langchain-ollama")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

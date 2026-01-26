#!/usr/bin/env python3
"""
04 - RAG QA (LCEL 版本)
学习检索增强生成（RAG）技术，通过文档检索来提高问答的准确性
"""

import os
from dotenv import load_dotenv

load_dotenv(override=True)


def main():
    print("🦜🔗 04 - RAG QA (LCEL)")
    print("=" * 40)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        from langchain_openai import ChatOpenAI, OpenAIEmbeddings
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_chroma import Chroma
        from langchain_community.document_loaders import TextLoader
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        print("✓ LangChain 组件导入完成")

        print("\n=== 1. 准备文档数据 ===")

        os.makedirs("temp_docs", exist_ok=True)

        sample_docs = [
            (
                "temp_docs/python_intro.txt",
                """
Python 是一种高级编程语言，由 Guido van Rossum 于 1991 年首次发布。
Python 具有简洁明了的语法，易于学习和使用，被广泛应用于 Web 开发、
数据科学、人工智能、自动化脚本等领域。

Python 的主要特点包括：
- 语法简洁，可读性强
- 支持多种编程范式（面向对象、函数式、过程式）
- 丰富的标准库和第三方库
- 跨平台，可在多种操作系统上运行
- 活跃的社区支持
""",
            ),
            (
                "temp_docs/langchain_intro.txt",
                """
LangChain 是一个用于构建基于大语言模型应用程序的框架。
它提供了一套工具和组件，帮助开发者更容易地创建复杂的 AI 应用。

LangChain 的核心功能包括：
- 模型抽象：统一不同 LLM 提供商的接口
- 提示词管理：创建和管理复杂的提示词模板
- 链式调用：将多个组件串联成工作流
- 记忆管理：为对话系统添加记忆功能
- 智能体：创建能够使用工具的自主智能体
- 索引和检索：构建 RAG 系统
""",
            ),
        ]

        for file_path, content in sample_docs:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip())

        print("✓ 示例文档创建完成")

        print("\n=== 2. 加载和分割文档 ===")

        all_documents = []
        for file_path, _ in sample_docs:
            loader = TextLoader(file_path, encoding="utf-8")
            docs = loader.load()
            all_documents.extend(docs)

        print(f"✓ 加载了 {len(all_documents)} 个文档")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, chunk_overlap=50
        )
        splits = text_splitter.split_documents(all_documents)
        print(f"✓ 文档分割完成，共 {len(splits)} 个分块")

        print("\n=== 3. 创建向量数据库 ===")

        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

        embeddings = OpenAIEmbeddings(api_key=SecretStr(api_key), base_url=base_url)
        vectorstore = Chroma.from_documents(
            documents=splits, embedding=embeddings, persist_directory="./chroma_db"
        )
        print("✓ 向量数据库创建完成")

        print("\n=== 4. 创建 RAG 问答链 (LCEL) ===")

        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(api_key),
            base_url=base_url,
        )

        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        prompt = ChatPromptTemplate.from_template(
            """基于以下上下文信息回答问题。如果上下文中没有相关信息，请说"根据提供的文档，我无法回答这个问题"。

上下文：
{context}

问题：{input}

请提供准确、详细的回答："""
        )

        def format_docs(docs):
            """格式化检索到的文档"""
            return "\n\n".join(doc.page_content for doc in docs)

        # LCEL RAG 链
        rag_chain = (
            {"context": retriever | format_docs, "input": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        print("✓ RAG 问答链创建完成")

        print("\n=== 5. 测试 RAG 问答 ===")

        test_questions = [
            "Python 有哪些主要特点？",
            "LangChain 提供哪些核心功能？",
            "Python 是谁创建的？",
        ]

        for question in test_questions:
            print(f"\n问题：{question}")
            result = rag_chain.invoke(question)
            print(f"回答：{result}")

        print("\n=== 6. 添加新文档 ===")

        new_content = """
深度学习是机器学习的一个子领域，它使用多层神经网络来学习数据的复杂模式。
深度学习在图像识别、自然语言处理、语音识别等领域取得了突破性进展。
常见的深度学习框架包括 TensorFlow、PyTorch、Keras 等。
"""

        with open("temp_docs/deep_learning.txt", "w", encoding="utf-8") as f:
            f.write(new_content.strip())

        new_loader = TextLoader("temp_docs/deep_learning.txt", encoding="utf-8")
        new_docs = new_loader.load()
        new_splits = text_splitter.split_documents(new_docs)
        vectorstore.add_documents(new_splits)

        print(f"✓ 添加了 {len(new_splits)} 个新的文档分块")

        print("\n问题：什么是深度学习？")
        result = rag_chain.invoke("什么是深度学习？")
        print(f"回答：{result}")

        print("\n🎉 RAG QA (LCEL) 示例运行成功！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

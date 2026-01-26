#!/usr/bin/env python3
"""
03 - Memory Chat
学习如何在 LangChain 中实现带记忆的对话系统
"""

import os
from dotenv import load_dotenv
from pydantic import SecretStr

# 加载环境变量
load_dotenv(override=True)


def main():
    print("🦜🔗 03 - Memory Chat")
    print("=" * 40)

    # 检查 API 密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        # 导入 LangChain 组件
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
        from langchain_core.messages import HumanMessage, AIMessage
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser

        print("✓ LangChain 组件导入完成")

        # 从环境变量读取配置
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

        # 初始化模型
        llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=SecretStr(api_key),
            base_url=base_url,
        )
        print("✓ 模型初始化完成")

        # 创建滑动窗口记忆（使用简单的列表存储）
        chat_history = []
        max_history = 5  # 保留最近 5 轮对话
        print("✓ 对话记忆创建完成")

        # 创建带记忆的提示词模板
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一个友好的 AI 助手，能够记住之前的对话内容。"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{input}"),
            ]
        )
        print("✓ 带记忆的提示词模板创建完成")

        # 创建 LCEL 链
        def format_chat_history(history):
            """格式化对话历史"""
            formatted = []
            for msg in history:
                if msg["type"] == "human":
                    formatted.append(HumanMessage(content=msg["content"]))
                elif msg["type"] == "ai":
                    formatted.append(AIMessage(content=msg["content"]))
            return formatted

        conversation = (
            RunnablePassthrough.assign(
                chat_history=lambda x: format_chat_history(x["chat_history"])
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        print("✓ 带记忆的对话链创建完成")

        # 测试对话
        print("\n=== 开始对话测试 ===")

        # 第一轮对话
        input1 = "你好！我叫小明，今年 25 岁。"
        response1 = conversation.invoke({"input": input1, "chat_history": chat_history})
        chat_history.append({"type": "human", "content": input1})
        chat_history.append({"type": "ai", "content": response1})
        print(f"用户：{input1}")
        print(f"AI：{response1}")

        # 第二轮对话
        input2 = "你还记得我的名字吗？"
        response2 = conversation.invoke({"input": input2, "chat_history": chat_history})
        chat_history.append({"type": "human", "content": input2})
        chat_history.append({"type": "ai", "content": response2})
        print(f"\n用户：{input2}")
        print(f"AI：{response2}")

        # 第三轮对话
        input3 = "我多大了？"
        response3 = conversation.invoke({"input": input3, "chat_history": chat_history})
        chat_history.append({"type": "human", "content": input3})
        chat_history.append({"type": "ai", "content": response3})
        print(f"\n用户：{input3}")
        print(f"AI：{response3}")

        # 查看记忆内容
        print("\n=== 当前记忆内容 ===")
        for i, msg in enumerate(chat_history):
            print(f"{i + 1}. {msg['type']}：{msg['content'][:50]}...")

        print(f"\n总共记忆了 {len(chat_history)} 条消息")

        print("\n🎉 Memory Chat 示例运行成功！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

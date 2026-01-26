#!/usr/bin/env python3
"""
02 - Prompt Template (LCEL 版本)
深入学习 LangChain 的提示词模板功能
"""

import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


def main():
    print("🦜🔗 02 - Prompt Template (LCEL)")
    print("=" * 40)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import (
            ChatPromptTemplate,
            SystemMessagePromptTemplate,
            HumanMessagePromptTemplate,
        )
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

        # 1. 基础提示词模板
        print("\n=== 1. 基础模板 ===")
        simple_template = ChatPromptTemplate.from_template("""
你是一个{role}。
请回答：{question}
""")

        chain = simple_template | llm | StrOutputParser()

        response = chain.invoke({
            "role": "Python 程序员",
            "question": "Python 的优势是什么？"
        })
        print(f"回答：{response}")

        print("\n=== 2. 结构化模板 + LCEL ===")
        system_template = SystemMessagePromptTemplate.from_template("""
你是一个专业的{role}。
你的任务是：{task}
请用{language}回答，保持{tone}的语调。
""")

        human_template = HumanMessagePromptTemplate.from_template("""
用户问题：{question}
""")

        chat_template = ChatPromptTemplate.from_messages(
            [system_template, human_template]
        )

        chain = chat_template | llm | StrOutputParser()

        response = chain.invoke({
            "role": "数据科学家",
            "task": "解释机器学习概念",
            "language": "中文",
            "tone": "专业且易懂",
            "question": "什么是过拟合？",
        })
        print(f"回答：{response}")

        print("\n=== 3. 多角色对比 + LCEL ===")
        roles = [
            {"role": "幼儿园老师", "tone": "耐心温柔", "language": "简单的中文"},
            {"role": "大学教授", "tone": "学术严谨", "language": "专业的中文"},
        ]

        question = "为什么天空是蓝色的？"

        for role_info in roles:
            print(f"\n--- {role_info['role']}的回答 ---")
            response = chain.invoke({
                "role": role_info["role"],
                "task": "解释自然现象",
                "language": role_info["language"],
                "tone": role_info["tone"],
                "question": question,
            })
            print(response)

        print("\n🎉 Prompt Template (LCEL) 示例运行成功！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

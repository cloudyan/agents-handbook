#!/usr/bin/env python3
"""
01 - Hello Chain
最简单的 LangChain 示例
"""

import os
from dotenv import load_dotenv

# 加载环境变量（覆盖全局环境变量）
load_dotenv(override=True)


def main():
    print("🦜🔗 01 - Hello Chain")
    print("=" * 40)

    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from pydantic import SecretStr

        print("✓ LangChain 组件导入完成")

        llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            api_key=SecretStr(api_key),
            base_url=base_url
        )
        print(f"✓ OpenAI 模型初始化完成 (model={model_name})")

        prompt_template = ChatPromptTemplate.from_template("""
你是一个友好的 AI 助手。请用中文回答用户的问题。

用户问题：{question}

请提供简洁而有用的回答：
""")
        print("✓ 提示词模板创建完成")

        chain = prompt_template | llm | StrOutputParser()
        print("✓ LCEL Chain 创建完成")

        question = "什么是 LangChain？请简单介绍一下。"
        print(f"\n问题：{question}")

        response = chain.invoke({"question": question})
        print(f"\n回答：{response}")

        print("\n🎉 Hello Chain 运行成功！")

    except ImportError as e:
        print(f"❌ 导入错误：{e}")
        print("请确保已安装所需依赖：pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ 运行错误：{e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

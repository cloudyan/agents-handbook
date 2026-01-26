#!/usr/bin/env python3
"""
08 - 结构化输出
使用 Pydantic 进行结构化数据提取和验证
"""

import os
import json
from typing import List, Optional
from datetime import datetime
from dataclasses import asdict
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv(override=True)


def example_1_basic_extraction():
    """示例 1: 基础信息提取"""
    print("\n" + "="*60)
    print("示例 1: 基础信息提取")
    print("="*60)

    from pydantic import BaseModel, Field, field_validator
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    class UserInfo(BaseModel):
        """用户信息模型"""
        name: str = Field(description="用户姓名")
        age: int = Field(description="用户年龄", ge=0, le=150)
        email: str = Field(description="用户邮箱")
        interests: List[str] = Field(description="用户兴趣列表")

        @field_validator('email')
        @classmethod
        def email_must_contain_at(cls, v):
            if '@' not in v:
                raise ValueError('邮箱必须包含 @ 符号')
            return v

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=SecretStr(openai_api_key),
        base_url=openai_base_url
    )
    parser = PydanticOutputParser(pydantic_object=UserInfo)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个信息提取专家，擅长从文本中提取结构化数据。"),
        ("user", """从以下文本中提取用户信息：
        {text}

        {format_instructions}
        """)
    ])

    chain = prompt | llm | parser

    test_text = """
    我叫李明，今年28岁，邮箱是liming@example.com。
    我的兴趣爱好包括编程、阅读和旅行。
    """

    try:
        result = chain.invoke({"text": test_text, "format_instructions": parser.get_format_instructions()})
        print(f"✓ 提取成功:")
        print(json.dumps(result.dict(), indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"✗ 提取失败: {e}")
        return None


def example_2_nested_models():
    """示例 2: 嵌套模型"""
    print("\n" + "="*60)
    print("示例 2: 嵌套模型")
    print("="*60)

    from pydantic import BaseModel, Field
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    class Address(BaseModel):
        """地址模型"""
        street: str = Field(description="街道地址")
        city: str = Field(description="城市")
        country: str = Field(description="国家")

    class Company(BaseModel):
        """公司信息模型"""
        name: str = Field(description="公司名称")
        industry: str = Field(description="所属行业")
        address: Address = Field(description="公司地址")

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=SecretStr(openai_api_key),
        base_url=openai_base_url
    )
    parser = PydanticOutputParser(pydantic_object=Company)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个信息提取专家。"),
        ("user", """从以下文本中提取公司信息：
        {text}

        {format_instructions}
        """)
    ])

    chain = prompt | llm | parser

    test_text = """
    科技创新有限公司是一家专注于人工智能的公司。
    公司位于北京市海淀区中关村大街1号，中国。
    """

    try:
        result = chain.invoke({"text": test_text, "format_instructions": parser.get_format_instructions()})
        print(f"✓ 提取成功:")
        print(json.dumps(result.dict(), indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"✗ 提取失败: {e}")
        return None


def example_3_event_extraction():
    """示例 3: 事件抽取"""
    print("\n" + "="*60)
    print("示例 3: 事件抽取")
    print("="*60)

    from pydantic import BaseModel, Field
    from typing import List
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    class Event(BaseModel):
        """事件模型"""
        title: str = Field(description="事件标题")
        date: str = Field(description="事件日期")
        location: str = Field(description="事件地点")
        participants: List[str] = Field(description="参与人员")
        description: str = Field(description="事件描述")

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=SecretStr(openai_api_key),
        base_url=openai_base_url
    )
    parser = PydanticOutputParser(pydantic_object=Event)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个事件信息提取专家。"),
        ("user", """从以下文本中提取事件信息：
        {text}

        {format_instructions}
        """)
    ])

    chain = prompt | llm | parser

    test_text = """
    2024年3月15日，在北京国际会议中心举办了人工智能技术峰会。
    张三、李四、王五等专家参加了会议。
    会议讨论了AI在医疗、教育等领域的应用前景。
    """

    try:
        result = chain.invoke({"text": test_text, "format_instructions": parser.get_format_instructions()})
        print(f"✓ 提取成功:")
        print(json.dumps(result.dict(), indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"✗ 提取失败: {e}")
        return None


def example_4_product_extraction():
    """示例 4: 产品信息提取"""
    print("\n" + "="*60)
    print("示例 4: 产品信息提取")
    print("="*60)

    from pydantic import BaseModel, Field
    from typing import Optional, List
    from enum import Enum
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    class ProductCategory(str, Enum):
        """产品类别枚举"""
        ELECTRONICS = "电子产品"
        CLOTHING = "服装"
        FOOD = "食品"
        BOOKS = "图书"

    class Product(BaseModel):
        """产品信息模型"""
        name: str = Field(description="产品名称")
        price: float = Field(description="产品价格", ge=0)
        category: ProductCategory = Field(description="产品类别")
        description: Optional[str] = Field(default=None, description="产品描述")
        features: List[str] = Field(description="产品特性列表")

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=SecretStr(openai_api_key),
        base_url=openai_base_url
    )
    parser = PydanticOutputParser(pydantic_object=Product)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个产品信息提取专家。"),
        ("user", """从以下文本中提取产品信息：
        {text}

        {format_instructions}
        """)
    ])

    chain = prompt | llm | parser

    test_text = """
    智能手机 X200，售价5999元。
    这是一款高性能电子产品，配备6.7英寸OLED屏幕、120Hz刷新率、5000万像素摄像头。
    支持5G网络，续航能力出色。
    """

    try:
        result = chain.invoke({"text": test_text, "format_instructions": parser.get_format_instructions()})
        print(f"✓ 提取成功:")
        print(json.dumps(result.dict(), indent=2, ensure_ascii=False))
        return result
    except Exception as e:
        print(f"✗ 提取失败: {e}")
        return None


def example_5_batch_extraction():
    """示例 5: 批量提取"""
    print("\n" + "="*60)
    print("示例 5: 批量提取")
    print("="*60)

    from pydantic import BaseModel, Field
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    class SimpleInfo(BaseModel):
        """简单信息模型"""
        name: str = Field(description="名称")
        value: str = Field(description="值")

    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=SecretStr(openai_api_key),
        base_url=openai_base_url
    )
    parser = PydanticOutputParser(pydantic_object=SimpleInfo)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个信息提取专家。"),
        ("user", """提取名称和值：
        {text}

        {format_instructions}
        """)
    ])

    chain = prompt | llm | parser

    test_texts = [
        "产品A价格100元",
        "服务B好评率95%",
        "用户C活跃度80",
    ]

    results = []
    for i, text in enumerate(test_texts, 1):
        try:
            result = chain.invoke({"text": text, "format_instructions": parser.get_format_instructions()})
            results.append(result)
            print(f"✓ 文本 {i}: {result.name} = {result.value}")
        except Exception as e:
            print(f"✗ 文本 {i} 失败: {e}")
            results.append(None)

    success_rate = sum(1 for r in results if r is not None) / len(results) * 100
    print(f"\n成功率: {success_rate:.1f}% ({sum(1 for r in results if r is not None)}/{len(results)})")


def example_6_comparison():
    """示例 6: 对比分析"""
    print("\n" + "="*60)
    print("示例 6: 结构化输出 vs 传统方法")
    print("="*60)

    from pydantic import BaseModel, Field
    from langchain_openai import ChatOpenAI
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    import re

    # 从环境变量读取配置
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    class ContactInfo(BaseModel):
        """联系信息模型"""
        name: str = Field(description="姓名")
        phone: str = Field(description="电话")
        email: str = Field(description="邮箱")

    test_text = """
    联系人：张伟
    电话：138-1234-5678
    邮箱：zhangwei@example.com
    """

    print("\n方法 1: 传统正则表达式")
    try:
        name_match = re.search(r'联系人[：:]\s*(\S+)', test_text)
        phone_match = re.search(r'电话[：:]\s*(\S+)', test_text)
        email_match = re.search(r'邮箱[：:]\s*(\S+)', test_text)

        regex_result = {
            "name": name_match.group(1) if name_match else None,
            "phone": phone_match.group(1) if phone_match else None,
            "email": email_match.group(1) if email_match else None
        }
        print(f"✓ 正则结果: {regex_result}")
    except Exception as e:
        print(f"✗ 正则失败: {e}")

    print("\n方法 2: 结构化输出")
    try:
        llm = ChatOpenAI(
            model=model_name,
            temperature=0,
            api_key=SecretStr(openai_api_key),
            base_url=openai_base_url
        )
        parser = PydanticOutputParser(pydantic_object=ContactInfo)

        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个信息提取专家。"),
            ("user", """提取联系信息：
            {text}

            {format_instructions}
            """)
        ])

        chain = prompt | llm | parser
        structured_result = chain.invoke({"text": test_text, "format_instructions": parser.get_format_instructions()})
        print(f"✓ 结构化结果: {structured_result.model_dump()}")
    except Exception as e:
        print(f"✗ 结构化失败: {e}")

    print("\n对比:")
    print("- 正则表达式：快速但需要精确模式，灵活性低")
    print("- 结构化输出：理解语义，灵活但需要 LLM 调用")


def main():
    """主函数"""
    print("🦜🔗 08 - 结构化输出")
    print("=" * 60)

    if not os.getenv("OPENAI_API_KEY"):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return 1

    try:
        example_1_basic_extraction()
        example_2_nested_models()
        example_3_event_extraction()
        example_4_product_extraction()
        example_5_batch_extraction()
        example_6_comparison()

        print("\n" + "="*60)
        print("🎉 结构化输出示例运行完成！")
        print("="*60)
        print("\n关键要点:")
        print("1. 使用 Pydantic 定义数据模型")
        print("2. 使用 PydanticOutputParser 进行解析")
        print("3. 添加字段描述和验证规则")
        print("4. 处理嵌套模型和复杂类型")
        print("5. 批量处理和错误处理")

    except Exception as e:
        print(f"❌ 运行错误：{e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())

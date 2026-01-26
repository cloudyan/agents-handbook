#!/usr/bin/env python3
"""
简单环境验证脚本
"""

import sys
import os


def main():
    print("🔍 LangChain Python 环境检查")
    print("=" * 50)

    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    else:
        print(f"✗ Python {version.major}.{version.minor}.{version.micro} (需要 ≥ 3.11)")
        return 1

    print("\n🔑 检查环境变量:")

    openai_key = os.getenv("OPENAI_API_KEY", "")
    if openai_key and openai_key != "your_openai_api_key_here" and len(openai_key) > 10:
        print("  ✓ OPENAI_API_KEY 已设置")
    else:
        print("  ✗ OPENAI_API_KEY 未设置或无效")
        print("  📝 请设置环境变量或创建 .env 文件")

    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    if base_url:
        print(f"  ✓ OPENAI_BASE_URL: {base_url}")
    else:
        print("  ℹ OPENAI_BASE_URL 使用默认值")

    model_name = os.getenv("MODEL_NAME", "")
    if model_name:
        print(f"  ✓ MODEL_NAME: {model_name}")
    else:
        print("  ℹ MODEL_NAME 使用默认值")

    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key and tavily_key != "your_tavily_api_key_here" and len(tavily_key) > 10:
        print("  ✓ TAVILY_API_KEY 已设置")
    else:
        print("  ℹ TAVILY_API_KEY 未设置 (搜索功能需要)")

    openweather_key = os.getenv("OPENWEATHER_API_KEY")
    if openweather_key and openweather_key != "your_openweather_api_key_here" and len(openweather_key) > 10:
        print("  ✓ OPENWEATHER_API_KEY 已设置")
    else:
        print("  ℹ OPENWEATHER_API_KEY 未设置 (天气功能需要)")

    print("\n📦 检查核心包:")
    packages = [
        "langchain",
        "langchain_openai",
        "langchain_community",
        "openai",
        "chromadb",
        "requests",
        "pandas",
        "fastapi",
    ]

    missing = []
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  ✓ {pkg}")
        except ImportError:
            print(f"  ✗ {pkg}")
            missing.append(pkg)

    print("\n" + "=" * 50)

    if missing:
        print("❌ 缺少依赖包，请运行:")
        print("   cd langchain-python")
        print("   uv sync")
        return 1

    print("🚀 环境检查通过！可以运行示例:")
    print("   cd langchain-python")
    print("   jupyter lab 01-hello-chain/")

    return 0


if __name__ == "__main__":
    sys.exit(main())

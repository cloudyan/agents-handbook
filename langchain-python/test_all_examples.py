#!/usr/bin/env python3
"""
测试所有示例脚本
验证导入和基本功能是否正常
"""

import os
import sys
from pathlib import Path


def test_public_modules():
    """测试公共模块"""
    print("\n=== 测试公共模块 ===")

    sys.path.insert(0, str(Path(__file__).parent))

    try:
        from clients import create_model_client, create_embedding_client, create_search_tool
        from utils import PerformanceMonitor, CustomCallbackHandler, setup_langsmith
        print("✓ 公共模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 公共模块导入失败: {e}")
        return False


def test_example_04():
    """测试 04-rag-qa"""
    print("\n=== 测试 04-rag-qa ===")

    try:
        import_path = Path(__file__).parent / "04-rag-qa" / "rag_qa.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("rag_qa", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["rag_qa"] = module
        spec.loader.exec_module(module)

        print("✓ 04-rag-qa 导入成功")
        return True
    except Exception as e:
        print(f"✗ 04-rag-qa 导入失败: {e}")
        return False


def test_example_05():
    """测试 05-agent-weather"""
    print("\n=== 测试 05-agent-weather ===")

    try:
        import_path = Path(__file__).parent / "05-agent-weather" / "agent_weather.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("agent_weather", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["agent_weather"] = module
        spec.loader.exec_module(module)

        print("✓ 05-agent-weather 导入成功")
        return True
    except Exception as e:
        print(f"✗ 05-agent-weather 导入失败: {e}")
        return False


def test_example_06():
    """测试 06-api-deployment"""
    print("\n=== 测试 06-api-deployment ===")

    try:
        import_path = Path(__file__).parent / "06-api-deployment" / "main.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("main", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["main"] = module
        spec.loader.exec_module(module)

        print("✓ 06-api-deployment 导入成功")
        return True
    except Exception as e:
        print(f"✗ 06-api-deployment 导入失败: {e}")
        return False


def test_example_07():
    """测试 07-advanced-agents"""
    print("\n=== 测试 07-advanced-agents ===")

    try:
        import_path = Path(__file__).parent / "07-advanced-agents" / "advanced_agents.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("advanced_agents", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["advanced_agents"] = module
        spec.loader.exec_module(module)

        print("✓ 07-advanced-agents 导入成功")
        return True
    except Exception as e:
        print(f"✗ 07-advanced-agents 导入失败: {e}")
        return False


def test_example_08():
    """测试 08-structured-output"""
    print("\n=== 测试 08-structured-output ===")

    try:
        import_path = Path(__file__).parent / "08-structured-output" / "structured_output.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("structured_output", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["structured_output"] = module
        spec.loader.exec_module(module)

        print("✓ 08-structured-output 导入成功")
        return True
    except Exception as e:
        print(f"✗ 08-structured-output 导入失败: {e}")
        return False


def test_example_09():
    """测试 09-multi-agent"""
    print("\n=== 测试 09-multi-agent ===")

    try:
        import_path = Path(__file__).parent / "09-multi-agent" / "multi_agent_system.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("multi_agent_system", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["multi_agent_system"] = module
        spec.loader.exec_module(module)

        print("✓ 09-multi-agent 导入成功")
        return True
    except Exception as e:
        print(f"✗ 09-multi-agent 导入失败: {e}")
        return False


def test_example_10():
    """测试 10-streaming-chat"""
    print("\n=== 测试 10-streaming-chat ===")

    try:
        import_path = Path(__file__).parent / "10-streaming-chat" / "chat_server.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("chat_server", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["chat_server"] = module
        spec.loader.exec_module(module)

        print("✓ 10-streaming-chat 导入成功")
        return True
    except Exception as e:
        print(f"✗ 10-streaming-chat 导入失败: {e}")
        return False


def test_example_11():
    """测试 11-production-tracing"""
    print("\n=== 测试 11-production-tracing ===")

    try:
        import_path = Path(__file__).parent / "11-production-tracing" / "tracing_example.py"
        if not import_path.exists():
            print(f"✗ 文件不存在: {import_path}")
            return False

        spec = __import__("importlib.util").util.spec_from_file_location("tracing_example", import_path)
        module = __import__("importlib.util").util.module_from_spec(spec)

        sys.modules["tracing_example"] = module
        spec.loader.exec_module(module)

        print("✓ 11-production-tracing 导入成功")
        return True
    except Exception as e:
        print(f"✗ 11-production-tracing 导入失败: {e}")
        return False


def main():
    print("🦜🔗 测试所有示例")
    print("=" * 60)

    os.chdir(Path(__file__).parent)

    results = {
        "公共模块": test_public_modules(),
        "04-rag-qa": test_example_04(),
        "05-agent-weather": test_example_05(),
        "06-api-deployment": test_example_06(),
        "07-advanced-agents": test_example_07(),
        "08-structured-output": test_example_08(),
        "09-multi-agent": test_example_09(),
        "10-streaming-chat": test_example_10(),
        "11-production-tracing": test_example_11(),
    }

    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    for name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name}: {status}")

    passed = sum(results.values())
    total = len(results)
    success_rate = (passed / total) * 100 if total > 0 else 0

    print(f"\n总计: {passed}/{total} 通过 ({success_rate:.1f}%)")

    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())

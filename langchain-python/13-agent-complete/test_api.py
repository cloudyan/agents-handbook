import asyncio
import httpx
import json


API_URL = "http://localhost:2025"


async def search_assistants() -> list:
    """搜索 assistants"""
    print("1️⃣ 搜索 assistants")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/assistants/search",
            json={"query": ""},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        assistants = response.json()

    print(f"找到 {len(assistants)} 个 assistants\n")
    return assistants


async def get_assistant_info(assistant_id: str) -> dict:
    """获取 assistant 信息"""
    print("2️⃣ 获取 assistant 信息")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_URL}/assistants/{assistant_id}")
        response.raise_for_status()
        assistant = response.json()

    print(json.dumps(assistant, indent=2, ensure_ascii=False))
    print()
    return assistant


async def create_thread() -> dict:
    """创建线程"""
    print("3️⃣ 创建线程")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/threads",
            json={},
            headers={"Content-Type": "application/json"},
        )
        response.raise_for_status()
        thread = response.json()

    print("创建线程成功\n")
    return thread


async def run_agent(assistant_id: str, thread_id: str, message: str):
    """运行 agent"""
    print(f"发送消息: {message}\n")

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{API_URL}/threads/{thread_id}/runs/stream",
            json={
                "assistant_id": assistant_id,
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": message,
                        }
                    ]
                },
            },
            headers={"Content-Type": "application/json"},
        ) as response:
            response.raise_for_status()

            assistant_response = ""

            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[6:].strip())

                        if data.get("event") == "values":
                            messages = data.get("data", {}).get("messages", [])
                            if messages:
                                last_msg = messages[-1]

                                if last_msg.get("tool_calls"):
                                    print("🔧 工具调用:")
                                    for call in last_msg["tool_calls"]:
                                        print(f"   - {call['name']}: {json.dumps(call['args'], ensure_ascii=False)}")

                                elif last_msg.get("role") == "assistant" and last_msg.get("content"):
                                    if not assistant_response:
                                        print("💬 助手回复:")
                                        assistant_response = last_msg["content"]
                                        print(assistant_response)

                    except (json.JSONDecodeError, KeyError):
                        pass

    print()


async def test_agent_complete():
    """测试完整版 Agent Chat 服务"""
    print("🧪 测试完整版 Agent Chat 服务")
    print("=========================\n")

    try:
        assistants = await search_assistants()
        assistant_id = assistants[0]["assistant_id"]
        print(f"Assistant ID: {assistant_id}\n")

        await get_assistant_info(assistant_id)

        thread = await create_thread()
        thread_id = thread["thread_id"]
        print(f"Thread ID: {thread_id}\n")

        print("📝 测试场景 1: 基础对话")
        await run_agent(assistant_id, thread_id, "你好，请介绍一下你自己")

        print("\n📝 测试场景 2: 数学计算")
        await run_agent(assistant_id, thread_id, "计算 25 * 4 + 10")

        print("\n📝 测试场景 3: 获取时间")
        await run_agent(assistant_id, thread_id, "现在几点了？")

        print("\n📝 测试场景 4: 天气查询")
        await run_agent(assistant_id, thread_id, "北京明天的天气怎么样？")

        print("\n📝 测试场景 5: 网络搜索")
        await run_agent(assistant_id, thread_id, "搜索最新的 AI 新闻")

        print("\n✅ 所有测试通过！")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_agent_complete())

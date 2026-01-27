"""09 - 多智能体协作系统 CLI 入口"""

import asyncio
from clients import create_model_client, create_search_tool
from agents import SupervisorAgent, ResearcherAgent, CoderAgent, ReviewerAgent


async def main():
    """主函数"""
    print("09 - 多智能体协作系统")
    print("="*60)

    llm = create_model_client()
    search_tool = create_search_tool()

    supervisor = SupervisorAgent(llm)
    supervisor.register_agent(ResearcherAgent(llm, search_tool))
    supervisor.register_agent(CoderAgent(llm))
    supervisor.register_agent(ReviewerAgent(llm))

    print("\n✓ 多智能体系统初始化完成\n")

    test_tasks = [
        "实现一个快速排序算法，使用 Python 实现",
        "研究 Python 的最佳实践",
    ]

    for task in test_tasks:
        result = await supervisor.coordinate_task(task)
        print(f"\n{'='*60}")
        print(f"📋 最终结果：")
        print("="*60)
        print(result)
        print("\n")

    print("多智能体协作系统运行完成！")


if __name__ == "__main__":
    asyncio.run(main())

"""LangGraph 工作流定义"""

import os
import sys
from pathlib import Path
from typing_extensions import TypedDict
from typing import Annotated, Sequence, Literal
from dotenv import load_dotenv
from pydantic import SecretStr
from langgraph.graph import StateGraph, END
import operator

sys.path.insert(0, str(Path(__file__).parent))

from clients import create_model_client, create_search_tool
from agents import SupervisorAgent, ResearcherAgent, CoderAgent, ReviewerAgent

load_dotenv(override=True)


class AgentState(TypedDict):
    """智能体状态"""
    messages: Annotated[Sequence, operator.add]
    task: str
    research_report: str
    code_content: str
    review_report: str
    task_type: str
    next_node: str


def get_llm():
    """获取 LLM 实例"""
    openai_api_key = os.getenv("OPENAI_API_KEY", "")
    openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    
    from langchain_openai import ChatOpenAI
    
    return ChatOpenAI(
        model=model_name,
        temperature=0,
        api_key=SecretStr(openai_api_key),
        base_url=openai_base_url,
    )


def get_supervisor():
    """获取 Supervisor 实例"""
    llm = get_llm()
    search_tool = create_search_tool()
    
    supervisor = SupervisorAgent(llm)
    supervisor.register_agent(ResearcherAgent(llm, search_tool))
    supervisor.register_agent(CoderAgent(llm))
    supervisor.register_agent(ReviewerAgent(llm))
    
    return supervisor


async def supervisor_node(state: AgentState) -> dict:
    """Supervisor 节点"""
    supervisor = get_supervisor()
    
    task = state.get("task", "")
    if not task and state.get("messages"):
        last_message = state["messages"][-1]
        if isinstance(last_message, dict):
            task = last_message.get("content", "")
    
    task_type = supervisor.analyze_task_type(task)
    
    if task_type == "code_development":
        return {"next_node": "researcher", "task_type": task_type, "task": task}
    elif task_type == "research":
        return {"next_node": "researcher", "task_type": task_type, "task": task}
    else:
        return {"next_node": "researcher", "task_type": task_type, "task": task}


async def researcher_node(state: AgentState) -> dict:
    """Researcher 节点"""
    supervisor = get_supervisor()
    
    if "Researcher" not in supervisor.agents:
        return {}
    
    researcher = supervisor.agents["Researcher"]
    task = state.get("task", "")
    if not task and state.get("messages"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, dict) and msg.get("content"):
                task = msg["content"]
                break
    
    if state.get("task_type") == "research":
        research_task = task
    else:
        research_task = f"研究如何{task}"
    
    research_message = researcher.send_message("Supervisor", research_task)
    research_response = await researcher.receive_message(research_message)
    
    if research_response:
        return {
            "research_report": research_response.content,
            "messages": [
                *state["messages"],
                {"role": "assistant", "content": f"[Researcher] {research_response.content[:200]}..."}
            ]
        }
    
    return {}


async def coder_node(state: AgentState) -> dict:
    """Coder 节点"""
    supervisor = get_supervisor()
    
    if "Coder" not in supervisor.agents:
        return {}
    
    coder = supervisor.agents["Coder"]
    task = state.get("task", "")
    research_report = state.get("research_report", "")
    
    if research_report:
        code_task = f"根据以下研究报告编写代码：\n\n{research_report}\n\n任务：{task}"
    else:
        code_task = task
    
    code_message = coder.send_message("Supervisor", code_task)
    code_response = await coder.receive_message(code_message)
    
    if code_response:
        return {
            "code_content": code_response.content,
            "messages": [
                *state["messages"],
                {"role": "assistant", "content": f"[Coder] {code_response.content[:200]}..."}
            ]
        }
    
    return {}


async def reviewer_node(state: AgentState) -> dict:
    """Reviewer 节点"""
    supervisor = get_supervisor()
    
    if "Reviewer" not in supervisor.agents or not state.get("code_content"):
        return {}
    
    reviewer = supervisor.agents["Reviewer"]
    review_message = reviewer.send_message("Supervisor", state["code_content"])
    review_response = await reviewer.receive_message(review_message)
    
    if review_response:
        return {
            "review_report": review_response.content,
            "messages": [
                *state["messages"],
                {"role": "assistant", "content": f"[Reviewer] {review_response.content[:200]}..."}
            ]
        }
    
    return {}


async def summary_node(state: AgentState) -> dict:
    """汇总节点"""
    results = [
        state.get("research_report"),
        state.get("code_content"),
        state.get("review_report")
    ]
    results = [r for r in results if r]
    
    task = state.get("task", "")
    if not task and state.get("messages"):
        for msg in reversed(state["messages"]):
            if isinstance(msg, dict) and msg.get("content"):
                task = msg["content"]
                break
    
    summary_prompt = f"""作为 Supervisor，请汇总以下任务执行结果：

用户任务：{task}

执行结果：
{chr(10).join([f"{i+1}. {r[:300]}..." for i, r in enumerate(results)])}

请提供：
1. 任务完成情况
2. 关键成果
3. 建议
4. 下一步行动"""
    
    llm = get_llm()
    response = await llm.ainvoke(summary_prompt)
    
    return {
        "messages": [
            *state["messages"],
            {"role": "assistant", "content": response.content}
        ]
    }


def should_go_to_coder(state: AgentState) -> Literal["coder", "summary"]:
    """判断是否转到 Coder"""
    return "coder" if state["task_type"] == "code_development" else "summary"


def should_go_to_reviewer(state: AgentState) -> Literal["reviewer", "summary"]:
    """判断是否转到 Reviewer"""
    return "reviewer" if state.get("code_content") else "summary"


def build_graph():
    """构建工作流图"""
    workflow = StateGraph(AgentState)
    
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("summary", summary_node)
    
    workflow.set_entry_point("supervisor")
    
    workflow.add_edge("supervisor", "researcher")
    
    workflow.add_conditional_edges(
        "researcher",
        should_go_to_coder,
        {
            "coder": "coder",
            "summary": "summary"
        }
    )
    
    workflow.add_conditional_edges(
        "coder",
        should_go_to_reviewer,
        {
            "reviewer": "reviewer",
            "summary": "summary"
        }
    )
    
    workflow.add_edge("reviewer", "summary")
    workflow.add_edge("summary", END)
    
    app = workflow.compile()
    
    return app


app = build_graph()

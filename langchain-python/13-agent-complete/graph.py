import os
import sys
from pathlib import Path
from typing import Annotated, List, Any
from typing_extensions import TypedDict
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

sys.path.insert(0, str(Path(__file__).parent))

from tools.index import tools

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
    temperature=0,
)


class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    tool_results: List[dict]
    reasoning: str


def analyze_node(state: AgentState) -> AgentState:
    """
    分析节点 - 分析问题并决定是否需要调用工具
    """
    system_prompt = """你是一个智能助手，可以使用工具帮助用户回答问题。

可用工具：
1. get_weather - 查询天气预报（需要城市名称）
2. search_web - 搜索网络信息（需要搜索关键词）
3. calculate - 计算数学表达式
4. get_current_time - 获取当前时间

工作流程：
1. 分析用户问题
2. 判断是否需要调用工具
3. 如果需要，选择合适的工具并生成工具调用
4. 如果不需要，直接回答问题

请用中文回答，提供准确和有用的信息。"""

    try:
        messages = [SystemMessage(content=system_prompt)]
        messages.extend(state["messages"])

        bound_llm = llm.bind_tools(tools)
        response = bound_llm.invoke(messages)

        content = response.content or ""
        tool_calls = response.tool_calls or []

        if not content and not tool_calls:
            return {
                **state,
                "messages": [AIMessage(content="抱歉，我无法处理这个问题。请尝试重新表述。")],
                "reasoning": "无法生成有效回复",
            }

        reasoning_msg = f"决定调用工具: {', '.join([t['name'] for t in tool_calls])}" if tool_calls else "直接回答用户问题"

        return {
            **state,
            "messages": [response],
            "reasoning": reasoning_msg,
        }

    except Exception as e:
        print(f"Analyze node error: {e}")
        return {
            **state,
            "messages": [AIMessage(content="处理您的请求时出现错误，请稍后重试。")],
            "reasoning": "处理失败",
        }


def execute_tools_node(state: AgentState) -> AgentState:
    """
    工具执行节点 - 执行工具调用
    """
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if not tool_calls:
        return {**state, "tool_results": []}

    tool_node = ToolNode(tools)
    result = tool_node.invoke({"messages": state["messages"]})

    tool_results = []
    for msg in result["messages"]:
        if isinstance(msg, ToolMessage):
            tool_results.append({
                "tool": msg.name,
                "result": msg.content,
            })

    return {
        **state,
        "messages": result["messages"],
        "tool_results": tool_results,
    }


def generate_answer_node(state: AgentState) -> AgentState:
    """
    回答生成节点 - 基于工具执行结果生成最终回答
    """
    system_prompt = """你是一个智能助手，基于工具执行结果为用户提供准确的答案。

工作流程：
1. 分析用户的原始问题
2. 结合工具执行结果
3. 生成清晰、准确、有用的回答
4. 如果工具执行失败，说明原因并提供建议

请用中文回答，保持友好和专业的语气。"""

    try:
        messages = [SystemMessage(content=system_prompt)]
        messages.extend(state["messages"])

        response = llm.invoke(messages)
        content = response.content or ""

        if not content:
            return {
                **state,
                "messages": [AIMessage(content="抱歉，我无法生成有效的回答。请稍后重试。")],
            }

        return {
            **state,
            "messages": [response],
        }

    except Exception as e:
        print(f"Generate answer node error: {e}")
        return {
            **state,
            "messages": [AIMessage(content="生成回答时出现错误，请稍后重试。")],
        }


def should_call_tools(state: AgentState) -> str:
    """
    条件边函数 - 决定下一步操作
    """
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    if tool_calls:
        return "execute_tools"
    return "end"


def create_graph():
    """
    创建工作流图
    """
    workflow = StateGraph(AgentState)

    workflow.add_node("analyze", analyze_node)
    workflow.add_node("execute_tools", execute_tools_node)
    workflow.add_node("generate_answer", generate_answer_node)

    workflow.set_entry_point("analyze")

    workflow.add_conditional_edges(
        "analyze",
        should_call_tools,
        {
            "execute_tools": "execute_tools",
            "end": END,
        },
    )

    workflow.add_edge("execute_tools", "generate_answer")
    workflow.add_edge("generate_answer", END)

    return workflow.compile()


app = create_graph()

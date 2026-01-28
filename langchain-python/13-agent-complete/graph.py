import json
import sys
from pathlib import Path
from typing import Annotated, List, Any, Dict
from typing_extensions import TypedDict
from langchain_core.messages import SystemMessage, convert_to_messages
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

sys.path.insert(0, str(Path(__file__).parent))

from tools.index import tools
from clients.model_client import create_model_client

llm_stream = create_model_client(temperature=0, streaming=True)
llm_fallback = create_model_client(temperature=0, streaming=False)
_STREAMING_ERROR = "No generations found in stream."


class AgentState(TypedDict):
    messages: Annotated[List[Any], add_messages]
    tool_results: List[Dict[str, str]]
    reasoning: str


def _ensure_list(value: Any) -> List[Any]:
    if not value:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _extract_tool_calls(message: Any) -> List[Dict[str, Any]]:
    if message is None:
        return []
    if isinstance(message, dict):
        return _ensure_list(message.get("tool_calls"))

    tool_calls = getattr(message, "tool_calls", None)
    if tool_calls:
        return _ensure_list(tool_calls)

    additional_kwargs = getattr(message, "additional_kwargs", None)
    if isinstance(additional_kwargs, dict):
        return _ensure_list(additional_kwargs.get("tool_calls"))

    return []


def _tool_call_field(tool_call: Any, key: str) -> Any:
    if isinstance(tool_call, dict):
        return tool_call.get(key)
    return getattr(tool_call, key, None)


def _normalize_tool_args(raw_args: Any) -> Any:
    if raw_args is None:
        return {}
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str):
        try:
            parsed = json.loads(raw_args)
        except json.JSONDecodeError:
            return raw_args
        return parsed if isinstance(parsed, dict) else str(parsed)
    return raw_args


def _invoke_with_fallback(
    primary_llm: Any,
    messages: List[Any],
    fallback_llm: Any | None = None,
) -> Any:
    try:
        return primary_llm.invoke(messages)
    except ValueError as exc:
        if str(exc) == _STREAMING_ERROR:
            target = fallback_llm or llm_fallback
            return target.invoke(messages)
        raise


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
        history_messages = convert_to_messages(state.get("messages", []))
        messages = [SystemMessage(content=system_prompt), *history_messages]

        bound_llm = llm_stream.bind_tools(tools)
        bound_fallback = llm_fallback.bind_tools(tools)
        response = _invoke_with_fallback(bound_llm, messages, fallback_llm=bound_fallback)

        content = response.content or ""
        tool_calls = _extract_tool_calls(response)

        if not content and not tool_calls:
            return {
                **state,
                "messages": [{"role": "assistant", "content": "抱歉，我无法处理这个问题。请尝试重新表述。"}],
                "reasoning": "无法生成有效回复",
            }

        tool_names = [
            str(name)
            for name in (_tool_call_field(call, "name") for call in tool_calls)
            if name
        ]
        reasoning_msg = (
            f"决定调用工具: {', '.join(tool_names)}" if tool_names else "直接回答用户问题"
        )

        return {
            **state,
            "messages": [{
                "role": "assistant",
                "content": content,
                "tool_calls": tool_calls
            }],
            "reasoning": reasoning_msg,
        }

    except Exception as e:
        print(f"Analyze node error: {e}")
        return {
            **state,
            "messages": [{"role": "assistant", "content": "处理您的请求时出现错误，请稍后重试。"}],
            "reasoning": "处理失败",
        }


def execute_tools_node(state: AgentState) -> AgentState:
    """
    工具执行节点 - 执行工具调用
    """
    last_message = state.get("messages", [])[-1] if state.get("messages") else None
    tool_calls = _extract_tool_calls(last_message)

    if not tool_calls:
        return {**state, "tool_results": []}

    tool_map = {tool.name: tool for tool in tools}
    tool_results = []
    tool_messages = []

    for index, tool_call in enumerate(tool_calls):
        tool_name = _tool_call_field(tool_call, "name")
        if not tool_name:
            continue
        tool = tool_map.get(tool_name)
        if tool:
            try:
                raw_args = _tool_call_field(tool_call, "args")
                args = _normalize_tool_args(raw_args)
                tool_call_id = (
                    _tool_call_field(tool_call, "id")
                    or _tool_call_field(tool_call, "tool_call_id")
                    or f"call_{index}"
                )
                result = tool.invoke(args)
                tool_results.append({
                    "tool": tool_name,
                    "result": str(result),
                })
                tool_messages.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": tool_call_id,
                })
            except Exception as e:
                print(f"Tool {tool_name} error: {e}")
                tool_results.append({
                    "tool": tool_name,
                    "result": f"工具执行失败: {str(e)}",
                })
                tool_messages.append({
                    "role": "tool",
                    "content": f"工具执行失败: {str(e)}",
                    "tool_call_id": tool_call_id,
                })

    return {
        **state,
        "messages": tool_messages,
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
        history_messages = convert_to_messages(state.get("messages", []))
        messages = [SystemMessage(content=system_prompt), *history_messages]

        response = _invoke_with_fallback(llm_stream, messages)
        content = response.content or ""

        if not content:
            return {
                **state,
                "messages": [{"role": "assistant", "content": "抱歉，我无法生成有效的回答。请稍后重试。"}],
            }

        return {
            **state,
            "messages": [{"role": "assistant", "content": content}],
        }

    except Exception as e:
        print(f"Generate answer node error: {e}")
        return {
            **state,
            "messages": [{"role": "assistant", "content": "生成回答时出现错误，请稍后重试。"}],
        }


def should_call_tools(state: AgentState) -> str:
    """
    条件边函数 - 决定下一步操作
    """
    last_message = state.get("messages", [])[-1] if state.get("messages") else None
    tool_calls = _extract_tool_calls(last_message)

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

import { StateGraph, END, Annotation } from "@langchain/langgraph";
import { createModelClient } from "../clients/model";
import { HumanMessage, SystemMessage, AIMessage, ToolMessage } from "@langchain/core/messages";
import { tools } from "./tools";

const llm = createModelClient({ streaming: true });

const StateAnnotation = Annotation.Root({
  messages: Annotation<Array<{ role: string; content: string; tool_calls?: any[]; tool_call_id?: string }>>({
    reducer: (x, y) => x.concat(y),
    default: () => [],
  }),
  tool_results: Annotation<Array<{ tool: string; result: string }>>({
    reducer: (x, y) => x.concat(y),
    default: () => [],
  }),
  reasoning: Annotation<string>({
    reducer: (x, y) => y ?? x ?? "",
    default: () => "",
  }),
});

/**
 * 分析节点 - 分析问题并决定是否需要调用工具
 */
async function analyzeNode(state: typeof StateAnnotation.State) {
  const systemPrompt = `你是一个智能助手，可以使用工具帮助用户回答问题。

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

请用中文回答，提供准确和有用的信息。`;

  try {
    const systemMsg = new SystemMessage(systemPrompt);

    const historyMessages = state.messages.map(msg => {
      if (msg.role === "user") {
        return new HumanMessage(msg.content);
      } else if (msg.role === "assistant") {
        const content = msg.content;
        const toolCalls = msg.tool_calls;

        if (toolCalls && toolCalls.length > 0) {
          return new AIMessage({
            content: content,
            tool_calls: toolCalls,
          });
        }
        return new AIMessage(content);
      }
      return msg;
    });

    const boundModel = llm.bindTools(tools);
    const response = await boundModel.invoke([systemMsg, ...historyMessages]);

    const content = response.content as string;
    const toolCalls = response.tool_calls;

    if (!content && (!toolCalls || toolCalls.length === 0)) {
      return {
        messages: [{
          role: "assistant",
          content: "抱歉，我无法处理这个问题。请尝试重新表述。"
        }],
        reasoning: "无法生成有效回复",
      };
    }

    return {
      messages: [{
        role: "assistant",
        content: content || "",
        tool_calls: toolCalls || []
      }],
      reasoning: toolCalls && toolCalls.length > 0
        ? `决定调用工具: ${toolCalls.map(t => t.name).join(", ")}`
        : "直接回答用户问题",
    };
  } catch (error) {
    console.error("Analyze node error:", error);
    return {
      messages: [{
        role: "assistant",
        content: "处理您的请求时出现错误，请稍后重试。"
      }],
      reasoning: "处理失败",
    };
  }
}

/**
 * 工具执行节点 - 执行工具调用
 */
async function executeToolsNode(state: typeof StateAnnotation.State) {
  const lastMessage = state.messages[state.messages.length - 1];
  const toolCalls = lastMessage?.tool_calls;

  if (!toolCalls || toolCalls.length === 0) {
    return { tool_results: [] };
  }

  const toolMap = new Map(tools.map(t => [t.name, t]));
  const results: Array<{ tool: string; result: string }> = [];

  for (const toolCall of toolCalls) {
    const tool = toolMap.get(toolCall.name);
    if (tool) {
      try {
        const result = await tool.invoke(toolCall.args);
        results.push({
          tool: toolCall.name,
          result: String(result),
        });

        state.messages.push({
          role: "tool",
          content: String(result),
          tool_call_id: toolCall.id,
        });
      } catch (error) {
        console.error(`Tool ${toolCall.name} error:`, error);
        results.push({
          tool: toolCall.name,
          result: `工具执行失败: ${error instanceof Error ? error.message : String(error)}`,
        });

        state.messages.push({
          role: "tool",
          content: `工具执行失败: ${error instanceof Error ? error.message : String(error)}`,
          tool_call_id: toolCall.id,
        });
      }
    }
  }

  return { tool_results: results };
}

/**
 * 回答生成节点 - 基于工具执行结果生成最终回答
 */
async function generateAnswerNode(state: typeof StateAnnotation.State) {
  const systemPrompt = `你是一个智能助手，基于工具执行结果为用户提供准确的答案。

工作流程：
1. 分析用户的原始问题
2. 结合工具执行结果
3. 生成清晰、准确、有用的回答
4. 如果工具执行失败，说明原因并提供建议

请用中文回答，保持友好和专业的语气。`;

  try {
    const systemMsg = new SystemMessage(systemPrompt);

    const historyMessages = state.messages.map(msg => {
      if (msg.role === "user") {
        return new HumanMessage(msg.content);
      } else if (msg.role === "assistant") {
        const content = msg.content;
        const toolCalls = msg.tool_calls;

        if (toolCalls && toolCalls.length > 0) {
          return new AIMessage({
            content: content,
            tool_calls: toolCalls,
          });
        }
        return new AIMessage(content);
      } else if (msg.role === "tool") {
        return new ToolMessage({
          content: msg.content,
          tool_call_id: msg.tool_call_id || "",
        });
      }
      return msg;
    });

    const response = await llm.invoke([systemMsg, ...historyMessages]);
    const content = response.content as string;

    if (!content) {
      return {
        messages: [{
          role: "assistant",
          content: "抱歉，我无法生成有效的回答。请稍后重试。"
        }],
      };
    }

    return {
      messages: [{
        role: "assistant",
        content: content
      }],
    };
  } catch (error) {
    console.error("Generate answer node error:", error);
    return {
      messages: [{
        role: "assistant",
        content: "生成回答时出现错误，请稍后重试。"
      }],
    };
  }
}

/**
 * 条件边函数 - 决定下一步操作
 */
function shouldCallTools(state: typeof StateAnnotation.State): string {
  const lastMessage = state.messages[state.messages.length - 1];
  const toolCalls = lastMessage?.tool_calls;

  if (toolCalls && toolCalls.length > 0) {
    return "execute_tools";
  }
  return "end";
}

/**
 * 创建工作流
 */
const workflow = new StateGraph(StateAnnotation)
  .addNode("analyze", analyzeNode)
  .addNode("execute_tools", executeToolsNode)
  .addNode("generate_answer", generateAnswerNode)
  .addEdge("__start__", "analyze")
  .addConditionalEdges(
    "analyze",
    shouldCallTools,
    {
      execute_tools: "execute_tools",
      end: END,
    }
  )
  .addEdge("execute_tools", "generate_answer")
  .addEdge("generate_answer", END);

export const app = workflow.compile();

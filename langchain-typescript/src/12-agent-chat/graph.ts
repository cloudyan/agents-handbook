import { StateGraph, END, Annotation } from "@langchain/langgraph";
import { createModelClient } from "../clients/model";
import { HumanMessage, SystemMessage, AIMessage } from "@langchain/core/messages";
import { tool } from "langchain";
import { z } from "zod";

const llm = createModelClient({ streaming: true });

const calculate = tool(
  async (input) => {
    try {
      const { expression } = input;
      const result = eval(expression);
      return `计算结果：${result}`;
    } catch {
      return "计算错误，请检查表达式";
    }
  },
  {
    name: "calculate",
    description: "计算数学表达式",
    schema: z.object({
      expression: z.string().describe("数学表达式，如 2 + 3 * 4"),
    }),
  }
);

const StateAnnotation = Annotation.Root({
  messages: Annotation<Array<{ role: string; content: string }>>({
    reducer: (x, y) => x.concat(y),
    default: () => [],
  }),
});

async function agentNode(state: typeof StateAnnotation.State) {
  const systemPrompt = "你是一个友好的AI助手，可以使用工具帮助用户。请用中文回答问题。";

  try {
    const systemMsg = new SystemMessage(systemPrompt);

    const historyMessages = state.messages.map(msg => {
      if (msg.role === "user") {
        return new HumanMessage(msg.content);
      } else if (msg.role === "assistant") {
        return new AIMessage(msg.content);
      }
      return msg;
    });

    const boundModel = llm.bindTools([calculate]);
    const response = await boundModel.invoke([systemMsg, ...historyMessages]);

    const content = response.content;

    if (!content) {
      throw new Error("LLM 返回空响应");
    }

    return {
      messages: [{ role: "assistant", content: String(content) }],
    };
  } catch (error) {
    console.error("Agent node error:", error);
    throw error;
  }
}

const workflow = new StateGraph(StateAnnotation)
  .addNode("agent", agentNode)
  .addEdge("__start__", "agent")
  .addEdge("agent", END);

export const app = workflow.compile();

import dotenv from "dotenv";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { tool } from "langchain";
import { z } from "zod";
import { createAgent } from "langchain";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "./clients/model";
import { createTracer, withTracking } from "./utils/monitor";

dotenv.config({ override: true });

const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

const calculator = tool(
  async (input: { expression: string }) => {
    try {
      const result = eval(input.expression);
      return `计算结果: ${result}`;
    } catch {
      return "计算错误";
    }
  },
  {
    name: "calculator",
    description: "计算数学表达式",
    schema: z.object({
      expression: z.string().describe("数学表达式，如 25 * 4"),
    }),
  }
);

async function example1SimpleChainWithTracing(
  tracer: ReturnType<typeof createTracer>
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 1: 简单 Chain 追踪");
  console.log("=".repeat(60));

  const { monitor, logger } = tracer;

  await withTracking("simple_chain", monitor, logger, async () => {
    const llm = createModelClient({
      temperature: 0,
    });

    const prompt = ChatPromptTemplate.fromTemplate("回答：{question}");

    const chain = prompt.pipe(llm).pipe(new StringOutputParser());

    const response = await chain.invoke(
      { question: "什么是 LangChain？" },
      {
        tags: ["production", "simple"],
        metadata: { version: "1.0", user_id: "demo" },
      }
    );

    console.log(`响应: ${response}`);
  });
}

async function example2AgentWithTracing(
  tracer: ReturnType<typeof createTracer>
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 2: Agent 追踪");
  console.log("=".repeat(60));

  const { monitor, logger } = tracer;

  await withTracking("agent_chain", monitor, logger, async () => {
    const llm = createModelClient({
      temperature: 0,
    });

    const tools = [calculator];

    const agent = createAgent({
      model: llm,
      tools,
      systemPrompt: "你是一个智能助手，可以使用计算器工具。",
    });

    const response = await agent.invoke(
      { messages: [new HumanMessage("计算 25 * 4 + 18 等于多少？")] },
      {
        tags: ["production", "agent"],
        metadata: { version: "1.0", agent_type: "calculator" },
      }
    );

    const content = response.messages[response.messages.length - 1].content as string;
    console.log(`响应: ${content}`);
  });
}

async function example3RAGWithTracing(
  tracer: ReturnType<typeof createTracer>
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 3: RAG 追踪");
  console.log("=".repeat(60));

  const { monitor, logger } = tracer;

  await withTracking("rag_chain", monitor, logger, async () => {
    const llm = createModelClient({
      temperature: 0,
    });

    const documents = [
      "LangChain 是一个用于构建 LLM 应用的框架。",
      "LangChain 提供了链式调用、提示词管理等功能。",
      "LangChain 支持多种 LLM 提供商和工具。",
    ];

    const prompt = ChatPromptTemplate.fromTemplate(`
基于以下上下文回答问题：

上下文：{context}

问题：{question}

回答：
`);

    const chain = prompt.pipe(llm).pipe(new StringOutputParser());

    const context = documents.join("\n");
    const response = await chain.invoke(
      { context, question: "LangChain 有什么功能？" },
      {
        tags: ["production", "rag"],
        metadata: { version: "1.0", retriever_type: "simple" },
      }
    );

    console.log(`响应: ${response}`);
  });
}

async function example4PerformanceComparison(
  tracer: ReturnType<typeof createTracer>
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 4: 性能对比");
  console.log("=".repeat(60));

  const { monitor, logger } = tracer;

  await withTracking(`model_${modelName}`, monitor, logger, async () => {
    const testQuestion = "什么是人工智能？";

    const llm = createModelClient({
      temperature: 0,
    });

    const response = await llm.invoke(testQuestion);

    console.log(`响应长度: ${response.content.toString().length} 字符`);
  });
}

async function main() {
  console.log("11 - 生产级追踪");
  console.log("=".repeat(60));

  const tracer = createTracer({
    autoSave: false,
  });

  try {
    await example1SimpleChainWithTracing(tracer);
    await example2AgentWithTracing(tracer);
    await example3RAGWithTracing(tracer);
    await example4PerformanceComparison(tracer);

    console.log("\n" + "=".repeat(60));
    console.log("性能摘要");
    console.log("=".repeat(60));

    const summary = tracer.monitor.getSummary();
    console.log(JSON.stringify(summary, null, 2));

    await tracer.monitor.saveMetrics();
    await tracer.logger.saveLogs();

    if (tracer.langsmithEnabled) {
      console.log("\n✓ 访问 LangSmith 查看详细追踪:");
      console.log("  https://smith.langchain.com/");
    }

    console.log("\n生产级追踪示例运行完成！");
  } catch (e) {
    console.log(`运行错误：${e}`);
    process.exit(1);
  }
}

main().catch(console.error);

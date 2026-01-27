
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { tool } from "langchain";
import { z } from "zod";
import { createAgent } from "langchain";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "./clients/model";

const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

interface PerformanceMetrics {
  chainName: string;
  executionTime: number;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  success: boolean;
  errorMessage: string;
}

class ProductionMonitor {
  metricsHistory: PerformanceMetrics[] = [];
  startTime: number | null = null;

  startTracking(): void {
    this.startTime = Date.now();
  }

  endTracking(
    chainName: string,
    success: boolean,
    error: string = ""
  ): PerformanceMetrics {
    if (!this.startTime) {
      throw new Error("必须先调用 startTracking()");
    }

    const executionTime = (Date.now() - this.startTime) / 1000;

    const metrics: PerformanceMetrics = {
      chainName,
      executionTime,
      inputTokens: 0,
      outputTokens: 0,
      totalTokens: 0,
      success,
      errorMessage: error,
    };

    this.metricsHistory.push(metrics);
    this.startTime = null;

    return metrics;
  }

  getSummary(): Record<string, unknown> {
    if (this.metricsHistory.length === 0) {
      return { message: "没有记录的指标" };
    }

    const totalRuns = this.metricsHistory.length;
    const successfulRuns = this.metricsHistory.filter((m) => m.success).length;
    const failedRuns = totalRuns - successfulRuns;

    const avgTime =
      this.metricsHistory.reduce((sum, m) => sum + m.executionTime, 0) / totalRuns;
    const totalTokens = this.metricsHistory.reduce((sum, m) => sum + m.totalTokens, 0);

    return {
      totalRuns,
      successfulRuns,
      failedRuns,
      successRate: successfulRuns / totalRuns,
      averageTime: avgTime,
      totalTokens,
      estimatedCost: totalTokens * 0.00002,
    };
  }

  saveMetrics(filename: string = "performance_metrics.json"): void {
    const data = {
      timestamp: new Date().toISOString(),
      summary: this.getSummary(),
      metrics: this.metricsHistory,
    };

    const fs = require("fs");
    fs.writeFileSync(filename, JSON.stringify(data, null, 2), "utf-8");
    console.log(`✓ 指标已保存到 ${filename}`);
  }
}

class CustomLogger {
  logs: string[] = [];

  log(level: string, message: string): void {
    const timestamp = new Date().toLocaleString("zh-CN");
    const logEntry = `[${timestamp}] [${level}] ${message}`;
    this.logs.push(logEntry);
    console.log(logEntry);
  }

  saveLogs(filename: string = "execution_logs.txt"): void {
    const fs = require("fs");
    fs.writeFileSync(filename, this.logs.join("\n"), "utf-8");
    console.log(`✓ 日志已保存到 ${filename}`);
  }
}

function setupLangsmith(): boolean {
  if (!langchainApiKey) {
    console.log("⚠️  未设置 LANGCHAIN_API_KEY，LangSmith 追踪已禁用");
    console.log("   访问 https://smith.langchain.com/ 获取 API Key");
    return false;
  }

  process.env.LANGCHAIN_TRACING_V2 = "true";
  process.env.LANGCHAIN_API_KEY = langchainApiKey;
  console.log("✓ LangSmith 追踪已启用");
  return true;
}

async function example1SimpleChainWithTracing(
  monitor: ProductionMonitor,
  logger: CustomLogger
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 1: 简单 Chain 追踪");
  console.log("=".repeat(60));

  try {
    const llm = createModelClient({
      temperature: 0,
    });

    const prompt = ChatPromptTemplate.fromTemplate("回答：{question}");

    const chain = prompt.pipe(llm).pipe(new StringOutputParser());

    monitor.startTracking();

    const response = await chain.invoke(
      { question: "什么是 LangChain？" },
      {
        tags: ["production", "simple"],
        metadata: { version: "1.0", user_id: "demo" },
      }
    );

    monitor.endTracking("simple_chain", true);
    console.log(`响应: ${response}`);
  } catch (e) {
    monitor.endTracking("simple_chain", false, e instanceof Error ? e.message : String(e));
    console.log(`错误: ${e}`);
    logger.log("ERROR", `简单 Chain 错误: ${e}`);
  }
}

async function example2AgentWithTracing(
  monitor: ProductionMonitor,
  logger: CustomLogger
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 2: Agent 追踪");
  console.log("=".repeat(60));

  try {
    const llm = createModelClient({
      temperature: 0,
    });

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

    const tools = [calculator];

    const agent = createAgent({
      model: llm,
      tools,
      systemPrompt: "你是一个智能助手，可以使用计算器工具。",
    });

    monitor.startTracking();

    const response = await agent.invoke(
      { messages: [new HumanMessage("计算 25 * 4 + 18 等于多少？")] },
      {
        tags: ["production", "agent"],
        metadata: { version: "1.0", agent_type: "calculator" },
      }
    );

    monitor.endTracking("agent_chain", true);
    const content = response.messages[response.messages.length - 1].content as string;
    console.log(`响应: ${content}`);
  } catch (e) {
    monitor.endTracking("agent_chain", false, e instanceof Error ? e.message : String(e));
    console.log(`错误: ${e}`);
    logger.log("ERROR", `Agent 错误: ${e}`);
  }
}

async function example3RAGWithTracing(
  monitor: ProductionMonitor,
  logger: CustomLogger
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 3: RAG 追踪");
  console.log("=".repeat(60));

  try {
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

    monitor.startTracking();

    const context = documents.join("\n");
    const response = await chain.invoke(
      { context, question: "LangChain 有什么功能？" },
      {
        tags: ["production", "rag"],
        metadata: { version: "1.0", retriever_type: "simple" },
      }
    );

    monitor.endTracking("rag_chain", true);
    console.log(`响应: ${response}`);
  } catch (e) {
    monitor.endTracking("rag_chain", false, e instanceof Error ? e.message : String(e));
    console.log(`错误: ${e}`);
    logger.log("ERROR", `RAG 错误: ${e}`);
  }
}

async function example4PerformanceComparison(
  monitor: ProductionMonitor,
  logger: CustomLogger
): Promise<void> {
  console.log("\n" + "=".repeat(60));
  console.log("示例 4: 性能对比");
  console.log("=".repeat(60));

  try {
    const testQuestion = "什么是人工智能？";

    const llm = createModelClient({
      temperature: 0,
    });

    monitor.startTracking();

    const response = await llm.invoke(testQuestion);

    monitor.endTracking(`model_${modelName}`, true);
    console.log(`响应长度: ${response.content.toString().length} 字符`);
  } catch (e) {
    monitor.endTracking(
      `model_${modelName}`,
      false,
      e instanceof Error ? e.message : String(e)
    );
    console.log(`错误: ${e}`);
    logger.log("ERROR", `性能对比错误: ${e}`);
  }
}

async function main() {
  console.log("11 - 生产级追踪");
  console.log("=".repeat(60));

  const langsmithEnabled = setupLangsmith();

  const monitor = new ProductionMonitor();
  const logger = new CustomLogger();

  try {
    await example1SimpleChainWithTracing(monitor, logger);
    await example2AgentWithTracing(monitor, logger);
    await example3RAGWithTracing(monitor, logger);
    await example4PerformanceComparison(monitor, logger);

    console.log("\n" + "=".repeat(60));
    console.log("性能摘要");
    console.log("=".repeat(60));

    const summary = monitor.getSummary();
    console.log(JSON.stringify(summary, null, 2));

    monitor.saveMetrics();
    logger.saveLogs();

    if (langsmithEnabled) {
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

import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { createModelClient } from "../../clients/model";
import { createTracer, withTracking } from ".";

async function exampleBasicUsage() {
  console.log("示例 1: 基础使用");
  console.log("=".repeat(60));

  const tracer = createTracer();

  withTracking("simple_chain", tracer.monitor, tracer.logger, async () => {
    const llm = createModelClient();
    const prompt = ChatPromptTemplate.fromTemplate("回答：{question}");
    const chain = prompt.pipe(llm).pipe(new StringOutputParser());

    const response = await chain.invoke({ question: "什么是 LangChain？" });
    console.log(`响应: ${response}`);
  });

  await tracer.monitor.saveMetrics();
  await tracer.logger.saveLogs();
}

async function exampleAdvancedUsage() {
  console.log("\n示例 2: 高级使用");
  console.log("=".repeat(60));

  const tracer = createTracer({
    autoSave: true,
    metricsFile: "advanced_metrics.json",
    logsFile: "advanced_logs.txt",
  });

  const llm = createModelClient();
  const prompt = ChatPromptTemplate.fromTemplate("回答：{question}");
  const chain = prompt.pipe(llm).pipe(new StringOutputParser());

  const questions = [
    "什么是 LangChain？",
    "LangChain 有什么功能？",
    "如何使用 LangChain？",
  ];

  for (const question of questions) {
    await withTracking(`question_${question.slice(0, 10)}`, tracer.monitor, tracer.logger, async () => {
      const response = await chain.invoke({ question });
      console.log(`\n问题: ${question}`);
      console.log(`回答: ${response.slice(0, 50)}...`);
    });
  }

  console.log("\n" + "=".repeat(60));
  console.log("性能摘要:");
  console.log("=".repeat(60));
  console.log(JSON.stringify(tracer.monitor.getSummary(), null, 2));
}

async function exampleErrorHandling() {
  console.log("\n示例 3: 错误处理");
  console.log("=".repeat(60));

  const tracer = createTracer();

  try {
    await withTracking("error_chain", tracer.monitor, tracer.logger, async () => {
      throw new Error("模拟的错误");
    });
  } catch (e) {
    console.log("错误已被捕获和记录");
  }

  const metrics = tracer.monitor.getMetrics();
  console.log("\n错误指标:");
  console.log(JSON.stringify(metrics, null, 2));
}

async function main() {
  await exampleBasicUsage();
  await exampleAdvancedUsage();
  await exampleErrorHandling();

  console.log("\n监控示例运行完成！");
}

main().catch(console.error);

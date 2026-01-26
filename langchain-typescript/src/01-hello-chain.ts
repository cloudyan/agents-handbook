import dotenv from "dotenv";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "@langchain/core/messages";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

async function helloChain() {
  console.log("🦜 Hello Chain - LangChain TypeScript 示例");
  console.log("=".repeat(50));

  const apiKey = process.env.OPENAI_API_KEY;
  const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
  const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

  if (!apiKey) {
    console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
    process.exit(1);
  }

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0.7,
    // verbose: true, // 如果需要调试信息，可以取消注释
  });

  const response = await llm.invoke([
    new HumanMessage("用一句话介绍 LangChain 是什么？"),
  ]).catch((error) => {
    console.error("❌ LLM 调用失败:", error);
    throw error;
  });

  console.log("\n📤 用户输入:");
  console.log("  用一句话介绍 LangChain 是什么？");

  console.log("\n📥 模型回复:");
  console.log(`  ${response.content}`);

  console.log("\n" + "=".repeat(50));
  console.log("✅ 示例运行完成！");
}

helloChain().catch(console.error);

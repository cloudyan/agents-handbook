import dotenv from "dotenv";
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

async function promptTemplate() {
  console.log("📝 提示词模板 - LangChain TypeScript 示例");
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
  });

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个专业的{topic}专家。请用简洁、专业的语言回答问题。"],
    ["human", "{input}"],
  ]);

  const chain = prompt.pipe(llm);

  console.log("\n📤 示例1: JavaScript 专家");
  console.log("-".repeat(50));
  const result1 = await chain.invoke({
    topic: "JavaScript",
    input: "什么是闭包？",
  });
  console.log(`📥 回答: ${result1.content}`);

  console.log("\n📤 示例2: Python 专家");
  console.log("-".repeat(50));
  const result2 = await chain.invoke({
    topic: "Python",
    input: "什么是装饰器？",
  });
  console.log(`📥 回答: ${result2.content}`);

  console.log("\n" + "=".repeat(50));
  console.log("✅ 示例运行完成！");
}

promptTemplate().catch(console.error);

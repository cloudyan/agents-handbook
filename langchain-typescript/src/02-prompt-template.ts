import dotenv from "dotenv";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { createModelClient } from "./clients/model";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

// 提示词模板
async function promptTemplate() {
  const model = createModelClient();

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个专业的{topic}专家。请用简洁、专业的语言回答问题。"],
    ["human", "{input}"],
  ]);

  const chain = prompt.pipe(model);

  console.log("\n示例1: JavaScript 专家");
  console.log("-".repeat(50));
  const result1 = await chain.invoke({
    topic: "JavaScript",
    input: "什么是闭包？",
  });
  console.log(`回答: ${result1.content}`);

  console.log("\n示例2: Python 专家");
  console.log("-".repeat(50));
  const result2 = await chain.invoke({
    topic: "Python",
    input: "什么是装饰器？",
  });
  console.log(`回答: ${result2.content}`);

  console.log("\n" + "=".repeat(50));
  console.log("示例运行完成！");
}

promptTemplate().catch(console.error);

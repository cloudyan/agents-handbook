import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "./clients/model";

// Hello Chain - LangChain TypeScript 示例
async function helloChain() {
  const model = createModelClient();

  const question = "什么是 LangChain？请简单介绍一下。";

  // 旧用法：直接调用 LLM
  // const response = await model.invoke([
  //   new HumanMessage(question),
  // ]).catch((error) => {
  //   console.error("LLM 调用失败:", error);
  //   throw error;
  // });

  // console.log("\n用户输入:");
  // console.log(question);
  // console.log("\n模型回复:");
  // console.log(`  ${response.content}`);


  // 新用法：使用 LCEL 链式调用(推荐)
  const prompt = ChatPromptTemplate.fromTemplate(`
你是一个友好的 AI 助手。请用中文回答用户的问题。

用户问题：{question}

请提供简洁而有用的回答：
`);

  // prompt: 传入用户问题
  // model: 调用语言模型
  // StringOutputParser: 将输出解析为字符串
  const chain = prompt.pipe(model).pipe(new StringOutputParser());

  console.log(`\n用户输入: ${question}`);

  const result = await chain.invoke({ question });

  console.log("\n模型回复:");
  console.log(`  ${result}`);


  console.log("示例运行完成！");
}

helloChain().catch(console.error);

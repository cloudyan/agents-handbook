import { createAgent } from "langchain";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "../clients/model"
import { readFile} from "../tools/read-file";
// import { writeFile } from "./tools/write-file";
import { getWeather } from "../tools/get-weather";
import { searchWeb } from "../tools/search-web";

const tools = [
  readFile,
  // writeFile,
  getWeather,
  searchWeb,
];

const llm = createModelClient();

const agent = createAgent({
  model: llm,
  tools,
  systemPrompt: `你是一个智能助理，能够使用各种工具来帮助用户完成任务。请根据用户的请求，选择合适的工具进行操作，并提供准确的回答。`,
});

export async function runAgent(input: string) {
  const response = await agent.invoke({
    messages: [new HumanMessage(input)],
  });
  return response;
}

// 示例用法
async function main() {
  const userInput = "上海的天气怎么样？";
  console.log("用户问题:", userInput);

  const response = await runAgent(userInput);
  const answer = response.messages[response.messages.length - 1].content;
  console.log("最终回答:", answer);
}

main().catch(console.error);

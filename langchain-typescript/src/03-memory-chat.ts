import dotenv from "dotenv";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { BaseMessage, HumanMessage, AIMessage } from "@langchain/core/messages";
import { createModelClient } from "./clients/model";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

class BufferMemory {
  private messages: BaseMessage[] = [];
  private maxMessages: number;

  constructor(maxMessages: number = 10) {
    this.maxMessages = maxMessages;
  }

  addMessage(message: BaseMessage): void {
    this.messages.push(message);
    if (this.messages.length > this.maxMessages) {
      this.messages = this.messages.slice(-this.maxMessages);
    }
  }

  getMessages(): BaseMessage[] {
    return this.messages;
  }

  clear(): void {
    this.messages = [];
  }
}

// 💬 带记忆的对话
async function memoryChat() {
  const model = createModelClient();

  const memory = new BufferMemory(5);

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个友好的助手，会记住之前的对话内容。"],
    ["placeholder", "{chat_history}"],
    ["human", "{input}"],
  ]);

  const chain = prompt.pipe(model);

  async function chat(userInput: string): Promise<void> {
    console.log(`\n你: ${userInput}`);

    const messages = memory.getMessages();
    const result = await chain.invoke({
      input: userInput,
      chat_history: messages,
    });

    const response = result.content as string;
    console.log(`助手: ${response}`);

    memory.addMessage(new HumanMessage(userInput));
    memory.addMessage(new AIMessage(response));
  }

  await chat("我叫小明");
  await chat("我今年25岁");
  await chat("我叫什么名字？");
  await chat("我多大了？");

  console.log("\n" + "=".repeat(50));
  console.log("对话完成！助手记住了你的信息。");
}

memoryChat().catch(console.error);

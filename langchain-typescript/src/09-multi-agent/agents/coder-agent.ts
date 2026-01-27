import { ChatOpenAI } from "@langchain/openai";
import { BaseAgent } from "./base-agent";
import { AgentMessage } from "../types";

export class CoderAgent extends BaseAgent {
  constructor(model: ChatOpenAI) {
    super("Coder", "代码编写和调试专家", model);
  }

  async processMessage(message: AgentMessage): Promise<AgentMessage | null> {
    const task = message.content;

    console.log(`\n[${this.name}] 接到任务：${task}`);

    const codingPrompt = `你是一个专业的程序员，擅长：
1. 编写高质量的代码
2. 遵循最佳实践
3. 添加清晰的注释
4. 优化代码性能

任务：${task}

请提供：
1. 完整的代码实现
2. 代码注释说明
3. 使用示例`;

    const response = await this.llm.invoke(codingPrompt);
    const codeContent = response.content as string;

    console.log(`[${this.name}] 代码编写完成`);
    console.log(`\n${"─".repeat(60)}`);
    console.log(`💻 [${this.name}] 代码实现：`);
    console.log("─".repeat(60));
    console.log(codeContent);
    console.log("─".repeat(60));
    console.log("\n".repeat(3));

    return this.sendMessage(
      message.sender,
      `代码实现：\n${codeContent}`
    );
  }
}

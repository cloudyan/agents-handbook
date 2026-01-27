import { ChatOpenAI } from "@langchain/openai";
import { Tool } from "@langchain/core/tools";
import { BaseAgent } from "./base-agent";
import { AgentMessage } from "./types";

export class ResearcherAgent extends BaseAgent {
  constructor(llm: ChatOpenAI, searchTool: Tool) {
    super("Researcher", "信息搜集和研究专家", llm, [searchTool]);
  }

  async processMessage(message: AgentMessage): Promise<AgentMessage | null> {
    const task = message.content;

    console.log(`\n[${this.name}] 接到任务：${task}`);

    const searchResult = await this.tools[0].invoke({ query: `${task} 技术细节` });

    const researchPrompt = `你是一个专业的研究助手，擅长：
1. 搜集和分析信息
2. 研究技术文档
3. 总结关键发现
4. 提供深入见解

任务：${task}
搜索结果：${searchResult}

请提供详细的研究报告，包括：
1. 核心概念
2. 关键技术点
3. 最佳实践
4. 注意事项`;

    const response = await this.llm.invoke(researchPrompt);
    const researchReport = response.content as string;

    console.log(`[${this.name}] 研究完成`);
    console.log(`\n${"─".repeat(60)}`);
    console.log(`📚 [${this.name}] 研究报告：`);
    console.log("─".repeat(60));
    console.log(researchReport);
    console.log("─".repeat(60));
    console.log("\n".repeat(3));

    return this.sendMessage(
      message.sender,
      `研究报告：\n${researchReport}`
    );
  }
}

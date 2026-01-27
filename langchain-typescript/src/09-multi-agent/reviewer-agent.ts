import { ChatOpenAI } from "@langchain/openai";
import { BaseAgent } from "./base-agent";
import { AgentMessage } from "./types";

export class ReviewerAgent extends BaseAgent {
  constructor(llm: ChatOpenAI) {
    super("Reviewer", "代码审查和质量检查专家", llm);
  }

  async processMessage(message: AgentMessage): Promise<AgentMessage | null> {
    const codeContent = message.content;

    console.log(`\n[${this.name}] 接到任务：审查代码`);

    const reviewPrompt = `你是一个专业的代码审查员，擅长：
1. 检查代码质量
2. 识别潜在问题
3. 提供改进建议
4. 评估代码性能

请审查以下内容：
${codeContent}

审查要点：
1. 代码正确性
2. 代码风格
3. 性能优化
4. 错误处理
5. 最佳实践

请提供详细的审查报告和改进建议。`;

    const response = await this.llm.invoke(reviewPrompt);
    const reviewReport = response.content as string;

    console.log(`[${this.name}] 审查完成`);
    console.log(`\n${"─".repeat(60)}`);
    console.log(`🔍 [${this.name}] 审查报告：`);
    console.log("─".repeat(60));
    console.log(reviewReport);
    console.log("─".repeat(60));
    console.log("\n".repeat(3));

    return this.sendMessage(
      message.sender,
      `审查报告：\n${reviewReport}`
    );
  }
}

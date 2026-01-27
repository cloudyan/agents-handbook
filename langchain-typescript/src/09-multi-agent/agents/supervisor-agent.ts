import { ChatOpenAI } from "@langchain/openai";
import { BaseAgent } from "./base-agent";

export class SupervisorAgent {
  name = "Supervisor";
  llm: ChatOpenAI;
  agents: Map<string, BaseAgent> = new Map();

  constructor(llm: ChatOpenAI) {
    this.llm = llm;
  }

  registerAgent(agent: BaseAgent): void {
    this.agents.set(agent.name, agent);
    console.log(`✓ 注册 Agent: ${agent.name} (${agent.role})`);
  }

  async coordinateTask(userRequest: string): Promise<string> {
    console.log(`\n${"=".repeat(60)}`);
    console.log(`🎯 用户请求：${userRequest}`);
    console.log("=".repeat(60));

    const taskType = this.analyzeTaskType(userRequest);

    if (taskType === "code_development") {
      return this.coordinateCodeDevelopment(userRequest);
    } else if (taskType === "research") {
      return this.coordinateResearch(userRequest);
    } else {
      return this.coordinateGeneralTask(userRequest);
    }
  }

  analyzeTaskType(task: string): string {
    const codeKeywords = ["实现", "编写", "代码", "函数", "算法", "程序"];
    const researchKeywords = ["研究", "分析", "比较", "调研", "技术"];

    const taskLower = task.toLowerCase();

    if (codeKeywords.some((kw) => taskLower.includes(kw))) {
      return "code_development";
    } else if (researchKeywords.some((kw) => taskLower.includes(kw))) {
      return "research";
    } else {
      return "general";
    }
  }

  private async coordinateCodeDevelopment(task: string): Promise<string> {
    const results: string[] = [];

    let researchReport = "";
    if (this.agents.has("Researcher")) {
      const researcher = this.agents.get("Researcher")!;
      const researchMessage = researcher.sendMessage("Supervisor", `研究如何${task}`);
      const researchResponse = await researcher.receiveMessage(researchMessage);
      if (researchResponse) {
        researchReport = researchResponse.content;
        results.push(researchReport);
        console.log(`\n[Supervisor] 收到研究报告`);
      }
    }

    let codeContent = "";
    if (this.agents.has("Coder")) {
      const coder = this.agents.get("Coder")!;
      const codeTask = researchReport
        ? `根据以下研究报告编写代码：\n\n${researchReport}\n\n任务：${task}`
        : task;
      const codeMessage = coder.sendMessage("Supervisor", codeTask);
      const codeResponse = await coder.receiveMessage(codeMessage);
      if (codeResponse) {
        codeContent = codeResponse.content;
        results.push(codeContent);
        console.log(`\n[Supervisor] 收到代码实现 (${codeContent.length} 字符)`);
      }
    }

    if (this.agents.has("Reviewer") && codeContent) {
      const reviewer = this.agents.get("Reviewer")!;
      const reviewMessage = reviewer.sendMessage("Supervisor", codeContent);
      const reviewResponse = await reviewer.receiveMessage(reviewMessage);
      if (reviewResponse) {
        results.push(reviewResponse.content);
        console.log(`\n[Supervisor] 收到审查报告`);
      }
    }

    const summary = await this.summarizeResults(task, results);
    return summary;
  }

  private async coordinateResearch(task: string): Promise<string> {
    const results: string[] = [];

    if (this.agents.has("Researcher")) {
      const researcher = this.agents.get("Researcher")!;
      const researchMessage = researcher.sendMessage("Supervisor", task);
      const researchResponse = await researcher.receiveMessage(researchMessage);
      if (researchResponse) {
        results.push(researchResponse.content);
        console.log(`\n[Supervisor] 收到研究结果`);
      }
    }

    const summary = await this.summarizeResults(task, results);
    return summary;
  }

  private async coordinateGeneralTask(task: string): Promise<string> {
    if (this.agents.has("Researcher")) {
      const researcher = this.agents.get("Researcher")!;
      const researchMessage = researcher.sendMessage("Supervisor", task);
      const researchResponse = await researcher.receiveMessage(researchMessage);
      if (researchResponse) {
        console.log(`\n[Supervisor] 收到研究结果`);
        return researchResponse.content;
      }
    }

    return "任务完成";
  }

  private async summarizeResults(task: string, results: string[]): Promise<string> {
    console.log(`\n[Supervisor] 汇总 ${results.length} 个结果`);

    const summaryPrompt = `作为 Supervisor，请汇总以下任务执行结果：

用户任务：${task}

执行结果：
${results.map((r, i) => `${i + 1}. ${r.slice(0, 300)}...`).join("\n")}

请提供：
1. 任务完成情况
2. 关键成果
3. 建议
4. 下一步行动`;

    const response = await this.llm.invoke(summaryPrompt);
    return response.content as string;
  }
}

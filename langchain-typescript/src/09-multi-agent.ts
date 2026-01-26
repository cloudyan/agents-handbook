import dotenv from "dotenv";
import { ChatOpenAI } from "@langchain/openai";
import { Tool } from "@langchain/core/tools";
import { z } from "zod";

dotenv.config({ override: true });

const apiKey = process.env.OPENAI_API_KEY;
const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

if (!apiKey) {
  console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
  process.exit(1);
}

interface AgentMessage {
  sender: string;
  receiver: string;
  content: string;
  context: Record<string, unknown>;
}

class BaseAgent {
  name: string;
  role: string;
  llm: ChatOpenAI;
  tools: Tool[];
  messageHistory: AgentMessage[] = [];

  constructor(name: string, role: string, llm: ChatOpenAI, tools: Tool[] = []) {
    this.name = name;
    this.role = role;
    this.llm = llm;
    this.tools = tools;
  }

  async receiveMessage(message: AgentMessage): Promise<AgentMessage | null> {
    this.messageHistory.push(message);
    return this.processMessage(message);
  }

  async processMessage(_message: AgentMessage): Promise<AgentMessage | null> {
    throw new Error("子类必须实现 processMessage 方法");
  }

  sendMessage(receiver: string, content: string, context: Record<string, unknown> = {}): AgentMessage {
    return {
      sender: this.name,
      receiver,
      content,
      context,
    };
  }
}

class ResearcherAgent extends BaseAgent {
  constructor(llm: ChatOpenAI, searchTool: Tool) {
    super("Researcher", "信息搜集和研究专家", llm, [searchTool]);
  }

  async processMessage(message: AgentMessage): Promise<AgentMessage | null> {
    const task = message.content;
    const context = message.context;

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

    return this.sendMessage(
      message.sender,
      `研究报告：\n${researchReport}`,
      { type: "research_result", original_task: task }
    );
  }
}

class CoderAgent extends BaseAgent {
  constructor(llm: ChatOpenAI) {
    super("Coder", "代码编写和调试专家", llm);
  }

  async processMessage(message: AgentMessage): Promise<AgentMessage | null> {
    const task = message.content;
    const context = message.context;

    console.log(`\n[${this.name}] 接到任务：${task}`);

    const researchContext = (context.research_result as string) || "";
    const codingPrompt = `你是一个专业的程序员，擅长：
1. 编写高质量的代码
2. 遵循最佳实践
3. 添加清晰的注释
4. 优化代码性能

任务：${task}

${researchContext ? `研究背景：\n${researchContext}\n` : ""}

请提供：
1. 完整的代码实现
2. 代码注释说明
3. 使用示例`;

    const response = await this.llm.invoke(codingPrompt);
    const codeContent = response.content as string;

    console.log(`[${this.name}] 代码编写完成`);

    return this.sendMessage(
      message.sender,
      `代码实现：\n${codeContent}`,
      { type: "code_result", original_task: task }
    );
  }
}

class ReviewerAgent extends BaseAgent {
  constructor(llm: ChatOpenAI) {
    super("Reviewer", "代码审查和质量检查专家", llm);
  }

  async processMessage(message: AgentMessage): Promise<AgentMessage | null> {
    const task = message.content;
    const context = message.context;

    console.log(`\n[${this.name}] 接到任务：审查代码`);

    const codeContent = (context.code_result as string) || task;

    const reviewPrompt = `你是一个专业的代码审查员，擅长：
1. 检查代码质量
2. 识别潜在问题
3. 提供改进建议
4. 评估代码性能

请审查以下代码：
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

    return this.sendMessage(
      message.sender,
      `审查报告：\n${reviewReport}`,
      { type: "review_result", original_task: task }
    );
  }
}

class SupervisorAgent {
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

  private analyzeTaskType(task: string): string {
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

    if (this.agents.has("Researcher")) {
      const researcher = this.agents.get("Researcher")!;
      const researchMessage = researcher.sendMessage("Researcher", `研究如何${task}`);
      const researchResponse = await researcher.receiveMessage(researchMessage);
      if (researchResponse) {
        results.push(researchResponse.content);
      }
    }

    if (this.agents.has("Coder")) {
      const coder = this.agents.get("Coder")!;
      const researchContext = results[results.length - 1] || "";
      const codeMessage = coder.sendMessage(
        "Coder",
        `实现${task}`,
        { research_result: researchContext }
      );
      const codeResponse = await coder.receiveMessage(codeMessage);
      if (codeResponse) {
        results.push(codeResponse.content);
      }
    }

    if (this.agents.has("Reviewer") && results.length >= 2) {
      const reviewer = this.agents.get("Reviewer")!;
      const reviewMessage = reviewer.sendMessage(
        "Reviewer",
        "审查代码",
        { code_result: results[results.length - 1] }
      );
      const reviewResponse = await reviewer.receiveMessage(reviewMessage);
      if (reviewResponse) {
        results.push(reviewResponse.content);
      }
    }

    const summary = await this.summarizeResults(task, results);
    return summary;
  }

  private async coordinateResearch(task: string): Promise<string> {
    const results: string[] = [];

    if (this.agents.has("Researcher")) {
      const researcher = this.agents.get("Researcher")!;
      const researchMessage = researcher.sendMessage("Researcher", task);
      const researchResponse = await researcher.receiveMessage(researchMessage);
      if (researchResponse) {
        results.push(researchResponse.content);
      }
    }

    const summary = await this.summarizeResults(task, results);
    return summary;
  }

  private async coordinateGeneralTask(task: string): Promise<string> {
    if (this.agents.has("Researcher")) {
      const researcher = this.agents.get("Researcher")!;
      const researchMessage = researcher.sendMessage("Researcher", task);
      const researchResponse = await researcher.receiveMessage(researchMessage);
      if (researchResponse) {
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

async function main() {
  console.log("🦜🔗 09 - 多智能体协作系统");
  console.log("=".repeat(60));

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const searchTool = new Tool({
    name: "search_database",
    description: "搜索工具（模拟）",
    schema: z.object({
      query: z.string().describe("搜索查询"),
    }),
    func: async (input: { query: string }) => {
      const knowledgeBase: Record<string, string> = {
        "快速排序": "快速排序是一种分治算法，平均时间复杂度 O(n log n)，通过选择基准元素分区实现。",
        "Python": "Python 是一种高级编程语言，语法简洁，适合快速开发。",
        "算法": "算法是解决特定问题的一系列明确步骤。",
        "代码优化": "代码优化包括时间复杂度优化、空间复杂度优化、代码可读性提升等。",
      };

      for (const [key, value] of Object.entries(knowledgeBase)) {
        if (input.query.includes(key)) {
          return `找到：${value}`;
        }
      }

      return `关于 '${input.query}' 的搜索结果：建议查阅官方文档和技术博客。`;
    },
  });

  const supervisor = new SupervisorAgent(llm);

  supervisor.registerAgent(new ResearcherAgent(llm, searchTool));
  supervisor.registerAgent(new CoderAgent(llm));
  supervisor.registerAgent(new ReviewerAgent(llm));

  console.log("\n✓ 多智能体系统初始化完成\n");

  const testTasks = [
    "实现一个快速排序算法",
    "研究 Python 的最佳实践",
  ];

  for (const task of testTasks) {
    const result = await supervisor.coordinateTask(task);
    console.log(`\n${"=".repeat(60)}`);
    console.log(`📋 最终结果：`);
    console.log("=".repeat(60));
    console.log(result);
    console.log("\n");
  }

  console.log("🎉 多智能体协作系统运行完成！");
}

main().catch(console.error);

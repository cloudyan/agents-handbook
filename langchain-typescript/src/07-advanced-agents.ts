import dotenv from "dotenv";
import { ChatOpenAI } from "@langchain/openai";
import { Tool } from "@langchain/core/tools";
import { z } from "zod";
import { AgentExecutor, createReactAgent } from "langchain/agents";
import { pull } from "langchain/hub";

dotenv.config({ override: true });

const apiKey = process.env.OPENAI_API_KEY;
const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

if (!apiKey) {
  console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
  process.exit(1);
}

async function advancedAgents() {
  console.log("🦜🔗 07 - Advanced Agents");
  console.log("=".repeat(50));

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  console.log("\n=== 1. ReAct Agent 示例 ===");

  const searchDatabase = new Tool({
    name: "search_database",
    description: "搜索数据库中的信息",
    schema: z.object({
      query: z.string().describe("搜索查询字符串"),
    }),
    func: async (input: { query: string }) => {
      const database: Record<string, string> = {
        "Python": "Python 是一种高级编程语言，由 Guido van Rossum 创建。",
        "机器学习": "机器学习是人工智能的一个分支，让计算机能够从数据中学习。",
        "LangChain": "LangChain 是用于构建 LLM 应用的框架。",
      };

      for (const [key, value] of Object.entries(database)) {
        if (input.query.toLowerCase().includes(key.toLowerCase())) {
          return `找到信息：${value}`;
        }
      }

      return "未找到相关信息";
    },
  });

  const calculate = new Tool({
    name: "calculate",
    description: "计算数学表达式",
    schema: z.object({
      expression: z.string().describe("数学表达式，如 2 + 3 * 4"),
    }),
    func: async (input: { expression: string }) => {
      try {
        const result = eval(input.expression);
        return `计算结果：${result}`;
      } catch {
        return "计算错误，请检查表达式";
      }
    },
  });

  const tools = [searchDatabase, calculate];

  const prompt = await pull("hwchase17/react");

  const agent = await createReactAgent({
    llm,
    tools,
    prompt,
  });

  const agentExecutor = new AgentExecutor({
    agent,
    tools,
    verbose: true,
  });

  console.log("测试 ReAct Agent:");
  const reactResponse = await agentExecutor.invoke({
    input: "Python 是什么？再计算一下 15 + 27 等于多少？",
  });
  console.log(`ReAct 回答：${reactResponse.output}`);

  console.log("\n=== 2. Plan-and-Execute 模式示例 ===");

  class PlanExecuteAgent {
    private llm: ChatOpenAI;
    private tools: Map<string, Tool>;

    constructor(llm: ChatOpenAI, tools: Tool[]) {
      this.llm = llm;
      this.tools = new Map();
      tools.forEach((tool) => this.tools.set(tool.name, tool));
    }

    async plan(goal: string): Promise<string[]> {
      const toolNames = Array.from(this.tools.keys()).join(", ");
      const prompt = `给定一个目标，制定一个详细的执行计划。列出需要执行的步骤。

目标：${goal}

可用工具：${toolNames}

请制定执行计划：`;

      const response = await this.llm.invoke(prompt);
      return ["搜索相关信息", "分析数据", "生成报告"];
    }

    async execute(plan: string[]): Promise<string> {
      const results: string[] = [];

      for (const step of plan) {
        console.log(`执行步骤：${step}`);

        if (step.includes("搜索")) {
          const searchTool = this.tools.get("search_database");
          if (searchTool) {
            const result = await searchTool.invoke({ query: "Python" });
            results.push(result);
          }
        } else if (step.includes("计算")) {
          const calcTool = this.tools.get("calculate");
          if (calcTool) {
            const result = await calcTool.invoke({ expression: "10 + 20" });
            results.push(result);
          }
        } else {
          results.push(`完成步骤：${step}`);
        }

        console.log(`结果：${results[results.length - 1]}`);
      }

      return results.join("\n");
    }

    async run(goal: string): Promise<string> {
      console.log(`目标：${goal}`);

      const plan = await this.plan(goal);
      console.log(`制定的计划：${plan}`);

      const result = await this.execute(plan);

      return `计划执行完成：\n${result}`;
    }
  }

  const planExecuteAgent = new PlanExecuteAgent(llm, tools);
  const planResult = await planExecuteAgent.run("研究 Python 并进行相关计算");
  console.log(`\nPlan-and-Execute 结果：\n${planResult}`);

  console.log("\n=== 3. Agent 性能对比 ===");

  const comparisonQuestions = [
    "什么是 Python？",
    "计算 25 * 4 等于多少？",
    "搜索 LangChain 的信息",
  ];

  console.log("\n--- ReAct Agent 测试 ---");
  for (const question of comparisonQuestions) {
    try {
      const response = await agentExecutor.invoke({ input: question });
      console.log(`Q: ${question}`);
      console.log(`A: ${response.output.slice(0, 100)}...`);
    } catch (e: unknown) {
      console.log(`错误：${e instanceof Error ? e.message : String(e)}`);
    }
  }

  console.log("\n🎉 高级 Agent 示例运行完成！");
}

advancedAgents().catch(console.error);

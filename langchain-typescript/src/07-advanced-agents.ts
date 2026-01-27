import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";
import { createAgent, tool } from "langchain";
import { HumanMessage } from "@langchain/core/messages";
import type { DynamicStructuredTool } from "@langchain/core/tools";
import { createModelClient } from "./clients/model";


const searchDatabase = tool(
  async (input: { query: string }) => {
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
  {
    name: "search_database",
    description: "搜索数据库中的信息",
    schema: z.object({
      query: z.string().describe("搜索查询字符串"),
    }),
  }
);

const calculate = tool(
  async (input: { expression: string }) => {
    try {
      const result = eval(input.expression);
      return `计算结果：${result}`;
    } catch {
      return "计算错误，请检查表达式";
    }
  },
  {
    name: "calculate",
    description: "计算数学表达式",
    schema: z.object({
      expression: z.string().describe("数学表达式，如 2 + 3 * 4"),
    }),
  }
);

class PlanExecuteAgent {
  private model: ChatOpenAI;
  private tools: Map<string, DynamicStructuredTool<any, any>>;
  private toolCallCount: number = 0;

  constructor(model: ChatOpenAI, tools: DynamicStructuredTool<any, any>[]) {
    this.model = model;
    this.tools = new Map();
    tools.forEach((t) => this.tools.set(t.name, t));
  }

  getToolCallCount(): number {
    return this.toolCallCount;
  }

  resetToolCallCount(): void {
    this.toolCallCount = 0;
  }

  // 规划阶段
  async plan(goal: string): Promise<string[]> {
    const toolNames = Array.from(this.tools.keys()).join(", ");
    const prompt = `给定一个目标，制定一个简洁的执行计划。只列出需要执行的关键步骤，每个步骤一行。

目标：${goal}

可用工具：${toolNames}

请按以下格式输出，只包含步骤编号和步骤描述：
1. 第一步
2. 第二步
3. 第三步

执行计划：`;

    const response = await this.model.invoke(prompt);
    const content = response.content as string;

    const steps = content
      .split("\n")
      .filter(line => line.trim().length > 0)
      .map(line => line.replace(/^\d+[\.\、]\s*/, "").trim())
      .filter(line => line.length > 5 && line.length < 100)
      .slice(0, 5);

    return steps.length > 0 ? steps : ["分析问题需求", "使用工具获取信息", "整理答案"];
  }

  // 执行阶段
  async execute(plan: string[], goal: string): Promise<string> {
    const toolResults: string[] = [];

    for (const step of plan) {
      const stepLower = step.toLowerCase();

      if (stepLower.includes("搜索") || stepLower.includes("search") || stepLower.includes("查询")) {
        const searchTool = this.tools.get("search_database");
        if (searchTool) {
          this.toolCallCount++;
          let query = goal;

          if (goal.toLowerCase().includes("python")) {
            query = "Python";
          } else if (goal.toLowerCase().includes("langchain")) {
            query = "LangChain";
          } else {
            query = goal.replace(/搜索|查询|信息|是什么|等/g, "").trim();
          }

          const result = await searchTool.invoke({ query });
          toolResults.push(result);
        }
      } else if (stepLower.includes("计算") || stepLower.includes("calculate") || /\d+[\+\-\*\/]\d+/.test(goal)) {
        const calcTool = this.tools.get("calculate");
        if (calcTool) {
          this.toolCallCount++;
          const exprMatch = goal.match(/\d+[\+\-\*\/]\d+/);
          const expr = exprMatch ? exprMatch[0] : goal.replace(/计算|等于|等/g, "").trim();
          const result = await calcTool.invoke({ expression: expr });
          toolResults.push(result);
        }
      }
    }

    if (toolResults.length === 0) {
      return "根据现有知识直接回答问题。";
    }

    const answerPrompt = `根据以下工具执行结果，生成最终答案：

目标：${goal}
工具结果：
${toolResults.map((r, i) => `${i + 1}. ${r}`).join("\n")}

请提供简洁、准确的答案：`;

    const finalResponse = await this.model.invoke(answerPrompt);
    return finalResponse.content as string;
  }

  async run(goal: string): Promise<{ result: string; steps: string[] }> {
    this.resetToolCallCount();

    const plan = await this.plan(goal);

    const result = await this.execute(plan, goal);

    return {
      result: `计划执行完成：\n${result}`,
      steps: plan
    };
  }
}

// Advanced Agents
// 理解 Agent 模式差异
//  * ReAct：适合实时交互、丰富解释、灵活推理的场景
//  * Plan-and-Execute：适合需要精确控制、系统化流程的复杂场景
// 培养 Agent 设计思维
//  * 何时使用框架内置模式
//  * 何时需要自定义实现
//  * 评估和比较不同 Agent 模式的性能
interface AgentTestResult {
  question: string;
  answer: string;
  toolCalls: number;
  success: boolean;
  steps?: string[];
}

async function advancedAgents() {
  const model = createModelClient();

  const tools = [searchDatabase, calculate];


  // ReAct 模式: 实时推理 + 工具调用，灵活但可能发散
  console.log("=== 1. ReAct 模式示例 ===");
  const agent = createAgent({
    model,
    tools,
    systemPrompt: "你是一个智能助手，可以使用工具来帮助用户回答问题。请根据用户的问题，决定是否需要调用工具，并给出最终答案。请用中文回答问题。",
  });

  const reactResponse = await agent.invoke({
    messages: [new HumanMessage("Python 是什么？再计算一下 15 + 27 等于多少？")],
  });
  console.log(`ReAct 回答：${reactResponse.messages[reactResponse.messages.length - 1].content}`);


  // Plan-and-Execute 模式: 先规划再执行，系统性强但不够灵活
  console.log("\n=== 2. Plan-and-Execute 模式示例 ===");

  const planExecuteAgent = new PlanExecuteAgent(model, tools as DynamicStructuredTool<any, any>[]);
  const planResult = await planExecuteAgent.run("研究 Python 并进行相关计算");
console.log(`\nPlan-and-Execute 结果：\n${planResult.result}`);
  console.log(`执行步骤：${planResult.steps.join(" → ")}`);


  console.log("\n=== 3. Self-Ask Agent 示例 ===");

  const webSearch = tool(
    async (input: { query: string }) => {
      const searchResults: Record<string, string> = {
        "LangChain 创建者": "LangChain 由 Harrison Chase 创建。",
        "LangChain 首次发布": "LangChain 于 2022 年首次发布。",
        "LangChain 功能": "LangChain 提供了 LLM 抽象、提示词管理、链式调用等功能。",
        "LangChain 版本": "LangChain 1.0 统一了 Agent API，引入了 LangGraph。",
      };

      for (const [key, value] of Object.entries(searchResults)) {
        if (input.query.toLowerCase().includes(key.toLowerCase())) {
          return value;
        }
      }

      return `关于 '${input.query}' 的搜索结果：未找到具体信息`;
    },
    {
      name: "web_search",
      description: "模拟网络搜索",
      schema: z.object({
        query: z.string().describe("搜索查询"),
      }),
    }
  );

  const selfAskAgent = createAgent({
    model,
    tools: [webSearch],
    systemPrompt: `你是一个智能助手，能够回答复杂问题。对于复杂问题，你会将其分解为子问题。

策略：
1. 识别问题中的关键信息需求
2. 将复杂问题分解为多个子问题
3. 逐步搜索答案
4. 综合得出最终答案

可用工具：
- web_search: 搜索网络信息

请用简洁明了的方式回答。`,
  });

  console.log("\n测试 Self-Ask Agent:");
  const selfAskQuestions = [
    "LangChain 是谁创建的？什么时候发布的？有什么功能？",
  ];

  for (const question of selfAskQuestions) {
    console.log(`\n问题：${question}`);
    const result = await selfAskAgent.invoke({
      messages: [new HumanMessage(question)],
    });
    console.log(`回答：${result.messages[result.messages.length - 1].content}`);
  }


  console.log("\n=== 4. Agent 性能对比 ===");
  const comparisonQuestions = [
    "什么是 Python？",
    "计算 25 * 4 等于多少？",
    "搜索 LangChain 的信息",
  ];

  const reactResults: AgentTestResult[] = [];
  const planResults: AgentTestResult[] = [];

  console.log("\n--- ReAct Agent 测试 ---");
  for (const question of comparisonQuestions) {
    try {
      const response = await agent.invoke({
        messages: [new HumanMessage(question)],
      });
      const content = response.messages[response.messages.length - 1].content as string;

      const toolCallPattern = /调用工具|使用工具|Tool call/i;
      const toolCalls = (content.match(toolCallPattern) || []).length;

      reactResults.push({
        question,
        answer: content,
        toolCalls,
        success: content.length > 10
      });

      console.log(`✓ ${question}`);
    } catch (e: unknown) {
      reactResults.push({
        question,
        answer: `错误：${e instanceof Error ? e.message : String(e)}`,
        toolCalls: 0,
        success: false
      });
      console.log(`✗ ${question}`);
    }
  }

  console.log("\n--- Plan-and-Execute Agent 测试 ---");
  for (const question of comparisonQuestions) {
    try {
      const result = await planExecuteAgent.run(question);

      planResults.push({
        question,
        answer: result.result,
        toolCalls: planExecuteAgent.getToolCallCount(),
        success: result.result.length > 10,
        steps: result.steps
      });

      console.log(`✓ ${question}`);
    } catch (e: unknown) {
      planResults.push({
        question,
        answer: `错误：${e instanceof Error ? e.message : String(e)}`,
        toolCalls: 0,
        success: false
      });
      console.log(`✗ ${question}`);
    }
  }

  console.log("\n=== 4. 对比结果汇总 ===");

  console.log("\n┌─────────────────────┬──────────────────┬──────────────────┬──────────────┬──────────────┐");
  console.log("│ 问题                │ ReAct 工具调用    │ Plan 工具调用    │ ReAct 成功率  │ Plan 成功率  │");
  console.log("├─────────────────────┼──────────────────┼──────────────────┼──────────────┼──────────────┤");

  for (let i = 0; i < comparisonQuestions.length; i++) {
    const react = reactResults[i];
    const plan = planResults[i];

    const q = comparisonQuestions[i].slice(0, 19).padEnd(19);
    const reactCalls = String(react.toolCalls).padEnd(16);
    const planCalls = String(plan.toolCalls).padEnd(16);
    const reactSuccess = react.success ? "✓ 成功".padEnd(12) : "✗ 失败".padEnd(12);
    const planSuccess = plan.success ? "✓ 成功" : "✗ 失败";

    console.log(`│ ${q} │ ${reactCalls} │ ${planCalls} │ ${reactSuccess} │ ${planSuccess} │`);
  }

  console.log("└─────────────────────┴──────────────────┴──────────────────┴──────────────┴──────────────┘");

  const reactTotalCalls = reactResults.reduce((sum, r) => sum + r.toolCalls, 0);
  const planTotalCalls = planResults.reduce((sum, r) => sum + r.toolCalls, 0);
  const reactSuccessRate = (reactResults.filter(r => r.success).length / reactResults.length * 100).toFixed(0);
  const planSuccessRate = (planResults.filter(r => r.success).length / planResults.length * 100).toFixed(0);

  console.log(`\n📊 统计汇总：`);
  console.log(`   ReAct Agent: 总工具调用 ${reactTotalCalls} 次, 成功率 ${reactSuccessRate}%`);
  console.log(`   Plan Agent:  总工具调用 ${planTotalCalls} 次, 成功率 ${planSuccessRate}%`);
  console.log(`   效率对比: ${reactTotalCalls < planTotalCalls ? "ReAct 更高效" : "Plan 更高效"}`);

  console.log("\n=== 6. 详细答案对比 ===\n");

  for (let i = 0; i < comparisonQuestions.length; i++) {
    console.log(`📌 问题 ${i + 1}: ${comparisonQuestions[i]}`);
    console.log(`\n  [ReAct]`);
    console.log(`  ${reactResults[i].answer.slice(0, 150)}${reactResults[i].answer.length > 150 ? "..." : ""}`);
    console.log(`\n  [Plan-and-Execute]`);
    console.log(`  ${planResults[i].answer.slice(0, 150)}${planResults[i].answer.length > 150 ? "..." : ""}`);
    if (planResults[i].steps) {
      console.log(`  步骤: ${planResults[i].steps.join("\n → ")}`);
    }
    console.log();
  }

  console.log("\n高级 Agent 示例运行完成！");
}

advancedAgents().catch(console.error);

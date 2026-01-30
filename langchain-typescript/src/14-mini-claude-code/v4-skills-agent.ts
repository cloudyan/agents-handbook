#!/usr/bin/env tsx
/**
 * Mini Claude Code v4 - Skills Mechanism
 *
 * 核心理念："知识外化"
 * ============================================
 * 技能是通过 SKILL.md 文件存储的知识。
 * 它们允许模型按需加载领域知识（如 PDF 处理、MCP 开发等）。
 */

import { createModelClient } from "../clients/model";
import { HumanMessage, ToolMessage, SystemMessage, BaseMessage } from "@langchain/core/messages";
import { bash } from "../tools/bash";
import { readFile } from "../tools/read-file";
import { writeFile } from "../tools/write-file";
import { editFile } from "../tools/edit-file";
import { todoWrite } from "../tools/todo-write";
import { createTaskTool, type AgentConfig } from "../tools/task";
import { createSkillTool } from "../tools/skill";
import { SKILLS } from "../skills/loader";
import * as readline from "readline";

const WORKDIR = process.cwd();

const AGENT_TYPES: Record<string, AgentConfig> = {
  explore: {
    description: "用于探索代码、查找文件、搜索的只读代理",
    tools: ["bash", "read_file"],
    prompt: "您是一个探索代理。搜索和分析，但绝不修改文件。返回一个简洁的摘要。",
  },
  code: {
    description: "用于实现功能和修复错误的全功能代理",
    tools: ["bash", "read_file", "write_file", "edit_file", "todo_write"],
    prompt: "您是一个编码代理。高效地实现请求的更改。",
  },
  plan: {
    description: "用于设计实现策略的规划代理",
    tools: ["bash", "read_file"],
    prompt: "您是一个规划代理。分析代码库并输出一个编号的实现计划。不要做更改。",
  },
};

function getAgentDescriptions(): string {
  return Object.entries(AGENT_TYPES)
    .map(([name, cfg]) => `- ${name}: ${cfg.description}`)
    .join("\n");
}

const baseTools = [bash, readFile, writeFile, editFile, todoWrite];

const taskTool = createTaskTool({
  tools: baseTools,
  createModel: () => createModelClient({ temperature: 0.1 }),
  workdir: WORKDIR,
  agentTypes: AGENT_TYPES
});

const skillTool = createSkillTool();

const allTools = [...baseTools, taskTool, skillTool];
const modelWithTools = createModelClient({ temperature: 0.1 }).bindTools(allTools);

const SYSTEM = `您是在 ${WORKDIR} 的编码代理。
可用技能：
${SKILLS.getDescriptions()}
可用子代理：
${getAgentDescriptions()}
规则：
- 当任务匹配技能描述时，立即使用 skill 工具加载技能
- 对于需要独立探索或实现的子任务，使用 task 工具
- 使用 todo_write 跟踪多步工作
- 优先使用工具而不是文字。行动，不要只是解释。
- 使用中文进行会话和思考。`;

async function agentLoop(history: BaseMessage[]) {
  try {
    while (true) {
      const res = await modelWithTools.invoke([new SystemMessage(SYSTEM), ...history]);
      if (res.content) {
        process.stdout.write(res.content as string);
      }
      history.push(res);

      if (!res.tool_calls?.length) return;

      for (const tc of res.tool_calls) {
        const selectedTool = allTools.find(t => t.name === tc.name);
        if (selectedTool) {
          if (tc.name === "task") {
            console.log(`\n> task: ${(tc.args as any).description}`);
          } else if (tc.name === "skill") {
            console.log(`\n> Loading skill: ${(tc.args as any).skill}`);
          } else {
            console.log(`\n> ${tc.name}`);
          }
          const output = await selectedTool.invoke(tc.args);
          if (tc.name !== "task") {
            const preview = output.length > 100 ? output.substring(0, 100) + "..." : output;
            console.log(`  结果预览: ${preview}`);
          }
          history.push(new ToolMessage({ tool_call_id: tc.id!, content: output }));
        }
      }
    }
  } catch (e: any) {
    console.error(`\n错误：API 调用失败。请检查您的 API Key 和配置。\n详情：${e.message || e}`);
  }
}

async function main() {
  console.log(`Mini Claude Code v4 (LangChain TS) - ${WORKDIR}`);
  console.log("输入 'exit' 退出。\n");

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const history: BaseMessage[] = [];

  const ask = () => rl.question("You: ", async (q) => {
    if (["exit", "quit", "q"].includes(q.toLowerCase()) || !q) {
      return rl.close();
    }
    history.push(new HumanMessage(q));
    await agentLoop(history);
    console.log("\n");
    ask();
  });
  ask();
}

// 测试： 使用 code-mentor 技能，分析 v4-skills-agent.ts 文件并总结其功能
main().catch(console.error);

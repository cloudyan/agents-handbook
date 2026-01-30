#!/usr/bin/env tsx
/**
 * Mini Claude Code v1 - 模型即代理
 *
 * 核心理念："模型即代理"
 * =========================================
 * 让模型调用工具直到完成的循环。这将聊天机器人转变为自主代理。
 *
 * 关键见解：模型是决策者。代码只是提供工具并运行循环。
 */

import { createModelClient } from "../clients/model";
import { HumanMessage, ToolMessage, SystemMessage, BaseMessage } from "@langchain/core/messages";
import { bash } from "../tools/bash";
import { readFile } from "../tools/read-file";
import { writeFile } from "../tools/write-file";
import { editFile } from "../tools/edit-file";
import * as readline from "readline";

const WORKDIR = process.cwd();

const tools = [bash, readFile, writeFile, editFile];
const model = createModelClient({ temperature: 0.1 });
const modelWithTools = model.bindTools(tools);

const SYSTEM = `您是在 ${WORKDIR} 的编码代理。
循环：简要思考 -> 使用工具 -> 报告结果。
规则：
- 优先使用工具而不是文字。行动，不要只是解释。
- 永远不要虚构文件路径。如果不确定，先使用 bash ls/find。
- 做最小更改。不要过度工程化。
- 完成后，总结更改了什么。
- 使用中文进行会话和思考。`;

// 核心代理循环
async function agentLoop(history: BaseMessage[]) {
  try {
    while (true) {
      const res = await modelWithTools.invoke([
        new SystemMessage(SYSTEM),
        ...history,
      ]);
      if (res.content) {
        process.stdout.write(res.content as string);
      }
      history.push(res);

      if (!res.tool_calls?.length) return;

      for (const tc of res.tool_calls) {
        const selectedTool = tools.find(t => t.name === tc.name);
        if (selectedTool) {
          const output = await selectedTool.invoke(tc.args);
          const preview = output.length > 100 ? output.substring(0, 100) + "..." : output;
          console.log(`\n  结果预览: ${preview}`);
          history.push(new ToolMessage({ tool_call_id: tc.id!, content: output }));
        }
      }
    }
  } catch (e: any) {
    console.error(`\n错误：API 调用失败。请检查您的 API Key 和配置。\n详情：${e.message || e}`);
  }
}

async function main() {
  console.log(`Mini Claude Code v1 (LangChain TS) - ${WORKDIR}`);
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

main().catch(console.error);

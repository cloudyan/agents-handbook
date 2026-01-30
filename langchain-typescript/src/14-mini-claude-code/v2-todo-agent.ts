#!/usr/bin/env tsx
/**
 * Mini Claude Code v2 - 结构化规划
 *
 * 核心理念："让计划可见"
 * =====================================
 * v2 添加了一个根本性改变代理工作方式的新工具：TodoWrite。
 * 现在你和模型都能看到计划。
 */

import { createModelClient } from "../clients/model";
import { HumanMessage, ToolMessage, SystemMessage, BaseMessage } from "@langchain/core/messages";
import { bash } from "../tools/bash";
import { readFile } from "../tools/read-file";
import { writeFile } from "../tools/write-file";
import { editFile } from "../tools/edit-file";
import { todoWrite } from "../tools/todo-write";
import * as readline from "readline";

const WORKDIR = process.cwd();

const tools = [bash, readFile, writeFile, editFile, todoWrite];
const model = createModelClient({ temperature: 0.1 });
const modelWithTools = model.bindTools(tools);

const SYSTEM = `您是在 ${WORKDIR} 的编码代理。
循环：规划 -> 使用工具行动 -> 更新待办事项 -> 报告。
规则：
- 使用 todo_write 跟踪多步骤任务
- 开始前标记任务为 in_progress，完成后标记为 completed
- 优先使用工具而不是文字。行动，不要只是解释。
- 完成后，总结更改了什么。
- 使用中文进行会话和思考。`;

const INITIAL_REMINDER = "<reminder>请使用 todo_write 来规划多步骤任务。</reminder>";
const NAG_REMINDER = "<reminder>您已经很多轮没有更新待办事项了。请更新待办事项以保持进度透明。</reminder>";

let roundsWithoutTodo = 0;

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

      let usedTodo = false;
      for (const tc of res.tool_calls) {
        const selectedTool = tools.find(t => t.name === tc.name);
        if (selectedTool) {
          if (tc.name === "todo_write") usedTodo = true;
          const output = await selectedTool.invoke(tc.args);
          const preview = output.length > 100 ? output.substring(0, 100) + "..." : output;
          console.log(`\n  结果预览: ${preview}`);
          history.push(new ToolMessage({ tool_call_id: tc.id!, content: output }));
        }
      }
      roundsWithoutTodo = usedTodo ? 0 : roundsWithoutTodo + 1;
    }
  } catch (e: any) {
    console.error(`\n错误：API 调用失败。请检查您的 API Key 和配置。\n详情：${e.message || e}`);
  }
}

async function main() {
  console.log(`Mini Claude Code v2 (LangChain TS) - ${WORKDIR}`);
  console.log("输入 'exit' 退出。\n");

  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  const history: BaseMessage[] = [];
  let firstMessage = true;

  const ask = () => rl.question("You: ", async (q) => {
    if (["exit", "quit", "q"].includes(q.toLowerCase()) || !q) {
      return rl.close();
    }

    let content = q;
    if (firstMessage) {
      content = `${INITIAL_REMINDER}\n${q}`;
      firstMessage = false;
    } else if (roundsWithoutTodo > 10) {
      content = `${NAG_REMINDER}\n${q}`;
    }

    history.push(new HumanMessage(content));
    await agentLoop(history);
    console.log("\n");
    ask();
  });
  ask();
}

main().catch(console.error);

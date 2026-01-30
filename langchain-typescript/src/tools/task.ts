import { tool } from "langchain";
import { z } from "zod";
import { HumanMessage, ToolMessage, SystemMessage, BaseMessage } from "@langchain/core/messages";

export interface AgentConfig {
  description: string;
  tools: string[];
  prompt: string;
}

export interface TaskToolConfig {
  tools: any[];
  createModel: () => any;
  workdir: string;
  agentTypes: Record<string, AgentConfig>;
}

export async function runTask(
  description: string,
  prompt: string,
  agentType: string,
  config: TaskToolConfig
): Promise<string> {
  const agentConfig = config.agentTypes[agentType];
  if (!agentConfig) {
    return `错误：未知代理类型 ${agentType}`;
  }

  console.log(`  [${agentType}] ${description}`);
  const subTools = config.tools.filter(t => agentConfig.tools.includes(t.name));
  const subModel = config.createModel().bindTools(subTools);
  const history: BaseMessage[] = [new HumanMessage(prompt)];
  const system = `您是在 ${config.workdir} 的 ${agentType} 子代理。\n\n${agentConfig.prompt}\n\n完成任务并返回一个清晰、简洁的摘要。`;

  let toolCount = 0;
  const start = Date.now();

  while (true) {
    const res = await subModel.invoke([new SystemMessage(system), ...history]);
    history.push(res);
    if (!res.tool_calls?.length) {
      console.log(`\n  [${agentType}] ${description} - 完成 (${toolCount} 个工具, ${((Date.now() - start) / 1000).toFixed(1)}s)`);
      return res.content as string;
    }

    for (const tc of res.tool_calls) {
      toolCount++;
      const selectedTool = subTools.find(t => t.name === tc.name);
      if (selectedTool) {
        const output = await (selectedTool as any).invoke(tc.args);
        history.push(new ToolMessage({ tool_call_id: tc.id!, content: output }));
      }
      process.stdout.write(`\r  [${agentType}] ${description} ... ${toolCount} 个工具, ${((Date.now() - start) / 1000).toFixed(1)}s`);
    }
  }
}

export function createTaskTool(config: TaskToolConfig) {
  return tool(
    async ({ description, prompt, agent_type }: { description: string; prompt: string; agent_type: string }) => {
      return await runTask(description, prompt, agent_type, config);
    },
    {
      name: "task",
      description: "生成一个子代理来处理集中的子任务。",
      schema: z.object({
        description: z.string().describe("任务的简短描述"),
        prompt: z.string().describe("子代理的详细指令"),
        agent_type: z.enum(["explore", "code", "plan"]).describe("代理类型")
      })
    }
  );
}

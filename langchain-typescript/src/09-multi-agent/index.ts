import { createModelClient } from "../clients/model";
import { createSearchTool } from "../clients/tavily";
import { SupervisorAgent } from "./agents/supervisor-agent";
import { ResearcherAgent } from "./agents/researcher-agent";
import { CoderAgent } from "./agents/coder-agent";
import { ReviewerAgent } from "./agents/reviewer-agent";

async function main() {
  console.log("09 - 多智能体协作系统");
  console.log("=".repeat(60));

  const llm = createModelClient();

  const searchTool = createSearchTool();

  const supervisor = new SupervisorAgent(llm);

  supervisor.registerAgent(new ResearcherAgent(llm, searchTool));
  supervisor.registerAgent(new CoderAgent(llm));
  supervisor.registerAgent(new ReviewerAgent(llm));

  console.log("\n✓ 多智能体系统初始化完成\n");

  const testTasks = [
    "实现一个快速排序算法，使用 JS 实现",
    // "实现算法计算 1=+...+100 的和",
    // "研究 Python 的最佳实践",
  ];

  for (const task of testTasks) {
    const result = await supervisor.coordinateTask(task);
    console.log(`\n${"=".repeat(60)}`);
    console.log(`📋 最终结果：`);
    console.log("=".repeat(60));
    console.log(result);
    console.log("\n");
  }

  console.log("多智能体协作系统运行完成！");
}

main().catch(console.error);

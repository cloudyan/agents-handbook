import { StateGraph, END } from "@langchain/langgraph";
import { createModelClient } from "../clients/model";
import { createSearchTool } from "../clients/tavily";
import { SupervisorAgent } from "./agents/supervisor-agent";
import { ResearcherAgent } from "./agents/researcher-agent";
import { CoderAgent } from "./agents/coder-agent";
import { ReviewerAgent } from "./agents/reviewer-agent";

interface AgentState {
  messages: Array<{ role: string; content: string }>;
  task: string;
  researchReport?: string;
  codeContent?: string;
  reviewReport?: string;
  taskType?: string;
  nextNode?: string;
}

const llm = createModelClient();
const searchTool = createSearchTool();

const supervisor = new SupervisorAgent(llm);

supervisor.registerAgent(new ResearcherAgent(llm, searchTool));
supervisor.registerAgent(new CoderAgent(llm));
supervisor.registerAgent(new ReviewerAgent(llm));

async function supervisorNode(state: AgentState): Promise<Partial<AgentState>> {
  const taskType = supervisor.analyzeTaskType(state.task);

  if (taskType === "code_development") {
    return { nextNode: "researcher", taskType };
  } else if (taskType === "research") {
    return { nextNode: "researcher", taskType };
  } else {
    return { nextNode: "researcher", taskType };
  }
}

async function researcherNode(state: AgentState): Promise<Partial<AgentState>> {
  if (!supervisor.agents.has("Researcher")) {
    return {};
  }

  const researcher = supervisor.agents.get("Researcher")!;
  const task = state.taskType === "code_development"
    ? `研究如何${state.task}`
    : state.task;

  const researchMessage = researcher.sendMessage("Supervisor", task);
  const researchResponse = await researcher.receiveMessage(researchMessage);

  if (researchResponse) {
    return {
      researchReport: researchResponse.content,
      messages: [
        ...state.messages,
        { role: "assistant", content: `[Researcher] ${researchResponse.content.slice(0, 200)}...` }
      ]
    };
  }

  return {};
}

async function coderNode(state: AgentState): Promise<Partial<AgentState>> {
  if (!supervisor.agents.has("Coder")) {
    return {};
  }

  const coder = supervisor.agents.get("Coder")!;
  const codeTask = state.researchReport
    ? `根据以下研究报告编写代码：\n\n${state.researchReport}\n\n任务：${state.task}`
    : state.task;

  const codeMessage = coder.sendMessage("Supervisor", codeTask);
  const codeResponse = await coder.receiveMessage(codeMessage);

  if (codeResponse) {
    return {
      codeContent: codeResponse.content,
      messages: [
        ...state.messages,
        { role: "assistant", content: `[Coder] ${codeResponse.content.slice(0, 200)}...` }
      ]
    };
  }

  return {};
}

async function reviewerNode(state: AgentState): Promise<Partial<AgentState>> {
  if (!supervisor.agents.has("Reviewer") || !state.codeContent) {
    return {};
  }

  const reviewer = supervisor.agents.get("Reviewer")!;
  const reviewMessage = reviewer.sendMessage("Supervisor", state.codeContent);
  const reviewResponse = await reviewer.receiveMessage(reviewMessage);

  if (reviewResponse) {
    return {
      reviewReport: reviewResponse.content,
      messages: [
        ...state.messages,
        { role: "assistant", content: `[Reviewer] ${reviewResponse.content.slice(0, 200)}...` }
      ]
    };
  }

  return {};
}

async function summaryNode(state: AgentState): Promise<Partial<AgentState>> {
  const results = [
    state.researchReport,
    state.codeContent,
    state.reviewReport
  ].filter(Boolean);

  const summaryPrompt = `作为 Supervisor，请汇总以下任务执行结果：

用户任务：${state.task}

执行结果：
${results.map((r, i) => `${i + 1}. ${r?.slice(0, 300)}...`).join("\n")}

请提供：
1. 任务完成情况
2. 关键成果
3. 建议
4. 下一步行动`;

  const response = await llm.invoke(summaryPrompt);

  return {
    messages: [
      ...state.messages,
      { role: "assistant", content: response.content as string }
    ]
  };
}

function shouldGoToCoder(state: AgentState): string {
  return state.taskType === "code_development" ? "coder" : "summary";
}

function shouldGoToReviewer(state: AgentState): string {
  return state.codeContent ? "reviewer" : "summary";
}

const workflow = new StateGraph<AgentState>({
  channels: {
    messages: {
      value: (x: AgentState["messages"], y?: AgentState["messages"]) => y ?? x,
      default: () => []
    },
    task: {
      value: (x: string, y?: string) => y ?? x,
      default: () => ""
    },
    researchReport: {
      value: (x: string | undefined, y?: string | undefined) => y ?? x ?? "",
      default: () => ""
    },
    codeContent: {
      value: (x: string | undefined, y?: string | undefined) => y ?? x ?? "",
      default: () => ""
    },
    reviewReport: {
      value: (x: string | undefined, y?: string | undefined) => y ?? x ?? "",
      default: () => ""
    },
    taskType: {
      value: (x: string | undefined, y?: string | undefined) => y ?? x ?? "",
      default: () => ""
    },
    nextNode: {
      value: (x: string | undefined, y?: string | undefined) => y ?? x ?? "",
      default: () => ""
    }
  }
})
  .addNode("supervisor", supervisorNode)
  .addNode("researcher", researcherNode)
  .addNode("coder", coderNode)
  .addNode("reviewer", reviewerNode)
  .addNode("summary", summaryNode)
  .addEdge("__start__", "supervisor")
  .addEdge("supervisor", "researcher")
  .addConditionalEdges("researcher", shouldGoToCoder, {
    coder: "coder",
    summary: "summary"
  })
  .addConditionalEdges("coder", shouldGoToReviewer, {
    reviewer: "reviewer",
    summary: "summary"
  })
  .addEdge("reviewer", "summary")
  .addEdge("summary", END);

export const app = workflow.compile();

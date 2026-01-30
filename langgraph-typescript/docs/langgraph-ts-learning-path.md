# LangGraph TypeScript 从入门到专家：学习路径与实战教程

本教程面向使用 TypeScript 的 LangGraph 开发者，从入门到生产实践循序渐进。内容参考 LangGraph 最新官方文档与本仓库示例，覆盖核心概念、最佳实践、架构设计与项目工程化建议。

## 学习路径概览

| 阶段 | 主题 | 产出 |
| --- | --- | --- |
| 0 | 环境准备 + 心智模型 | 能运行 Quickstart，理解 Graph/State/Node/Edge |
| 1 | 基础图（Graph API） | 搭建第一个可运行的图与工具调用 |
| 2 | 路由与循环 | 用条件边实现分支、回环与终止 |
| 3 | 类型安全状态与结构化输出 | 使用 Zod 与 Reducer 让状态可控 |
| 4 | 记忆与持久化 | 用 checkpointer 让会话可恢复 |
| 5 | 人工介入与审批 | 使用 interrupt/Command 构建 HITL |
| 6 | Streaming 与客户端集成 | 使用 SDK 获取流式事件 |
| 7 | 子图与多智能体 | 组合多个子图形成协作体系 |
| 8 | Functional API 与并发 | 用 task/entrypoint 写并行工作流 |
| 9 | 生产级架构与可观测 | 结构化工程、测试、部署、观测 |

---

## 阶段 0：环境准备与快速验证

### 目标
- 跑通最小可用示例
- 形成对 LangGraph 的基本心智模型

### 必备环境
- Node.js 18+（建议与 `langgraph.json` 指定版本一致）
- pnpm
- OpenAI API Key（示例默认使用 `OPENAI_API_KEY`）

### 快速启动

```bash
pnpm install
pnpm quickstart:server
pnpm quickstart:client
```

本仓库 `src/01-quick-start/agent.ts` 与 `src/01-quick-start/client.ts` 是最小图与 SDK 客户端的参考。

### 本地开发（LangGraph CLI）

使用 `@langchain/langgraph-cli` 可以本地启动 Graph 服务，结合 `langgraph.json` 暴露图给客户端调用。

```bash
pnpm quickstart:server
```

对应配置见 `src/01-quick-start/langgraph.json`。

---

## 阶段 1：第一个 Graph（Graph API）

### 核心概念
- **StateGraph**：声明图结构
- **StateSchema / MessagesValue / ReducedValue**：定义状态与 reducer
- **Node**：业务逻辑单元
- **Edge**：控制流

### State 建模方式（Graph API）
- **StateSchema**：直观的对象式定义，适合快速上手
- **Annotation / MessagesAnnotation**：更灵活的 reducer 组合与类型推导
- **MessagesZodState**：用 Zod 描述 messages 状态的预置方案

```ts
import { MessagesAnnotation, StateGraph, START, END } from "@langchain/langgraph";

const graph = new StateGraph(MessagesAnnotation)
  .addNode("llmCall", async () => ({ messages: [] }))
  .addEdge(START, "llmCall")
  .addEdge("llmCall", END)
  .compile();
```

### 最小示例骨架

```ts
import {
  StateGraph,
  StateSchema,
  MessagesValue,
  ReducedValue,
  START,
  END,
} from "@langchain/langgraph";
import { z } from "zod";

const MessagesState = new StateSchema({
  messages: MessagesValue,
  llmCalls: new ReducedValue(z.number().default(0), { reducer: (x, y) => x + y }),
});

const app = new StateGraph(MessagesState)
  .addNode("llmCall", async (state) => {
    // 调用 LLM，返回 { messages: [...] , llmCalls: 1 }
    return { messages: [], llmCalls: 1 };
  })
  .addEdge(START, "llmCall")
  .addEdge("llmCall", END)
  .compile();
```

### 实践任务
- 运行 `src/01-quick-start/agent.ts`，理解工具调用循环
- 修改 system prompt，观察模型对工具调用策略的变化

---

## 阶段 2：路由、分支与循环

### 关键点
- **条件边**：`addConditionalEdges` + 路由函数
- **循环**：节点之间形成闭环（如 LLM → Tool → LLM）
- **终止条件**：返回 `END` 停止

### 实践任务
参考 `src/03-chaining/agent.ts`，构建「质量检查→改写→润色」的链路。

---

## 阶段 3：类型安全状态与结构化输出

### 推荐实践
- 用 Zod 或 Annotation 描述状态结构，统一状态更新入口
- 用 `withStructuredOutput` 让模型输出结构化数据
- 通过 reducer 合并状态，避免污染原始数据

```ts
import { MessagesZodState, StateGraph, START, END } from "@langchain/langgraph";

const graph = new StateGraph(MessagesZodState)
  .addNode("llmCall", async () => ({ messages: [] }))
  .addEdge(START, "llmCall")
  .addEdge("llmCall", END)
  .compile();
```

### 实践任务
为邮件分类场景添加结构化分类结果，参考 `src/02-email-agent/README.md` 中的 schema。

---

## 阶段 4：记忆与持久化

### 核心概念
- **checkpointer**：保存图的执行状态
- **thread_id**：同一会话多次调用可恢复上下文
- **store**：跨会话的长期记忆或知识存储
- **Time Travel**：定位并回放历史状态（用于调试）

### 示例思路
在编译图时注入 `MemorySaver`，并通过 `configurable.thread_id` 来识别会话。

```ts
import { MemorySaver } from "@langchain/langgraph";

const memory = new MemorySaver();
const app = workflow.compile({ checkpointer: memory });
const config = { configurable: { thread_id: "user_123" } };

await app.invoke(input, config);
```

需要自定义 checkpointer 时，可单独安装 `@langchain/langgraph-checkpoint`。

---

## 阶段 5：人类在环（Human-in-the-Loop）

### 关键点
- 使用 `interrupt` 暂停执行并等待人工输入
- 通过 `Command` 完成恢复与状态更新
- 避免在 `interrupt` 附近使用捕获异常的 try/catch

### 实践任务
在邮件代理中加入人工审核节点，参考 `src/02-email-agent/README.md` 的流程图。

```ts
import { interrupt, Command } from "@langchain/langgraph";

const decision = interrupt({
  emailId: state.emailId,
  draft: state.responseText,
  action: "Please review and approve",
});

if (decision.approved) {
  return new Command({ goto: "sendReply" });
}
```

---

## 阶段 6：Streaming 与客户端集成

### 关键点
- `stream` 输出结构化事件
- 使用 `@langchain/langgraph-sdk` 订阅流式运行

### 示例（SDK）

```ts
import { Client } from "@langchain/langgraph-sdk";

const client = new Client({ apiUrl: "http://localhost:2024" });
const stream = client.runs.stream(null, "agent", {
  input: { messages: [{ role: "user", content: "What is LangGraph?" }] },
  streamMode: "messages-tuple",
});

for await (const chunk of stream) {
  console.log(chunk.event, chunk.data);
}
```

---

## 阶段 7：子图与多智能体协作

### 核心模式
- **Router → Expert**：路由图分发给专业子图
- **Supervisor → Worker**：监督者决策，工作者执行
- **Subgraph 复用**：复杂任务拆成小图拼装

### 实践任务
将「检索问答」「写作润色」「审批」拆成子图，再组合成主图。

---

## 阶段 8：Functional API 与并发工作流

### 适用场景
- 任务并行、批处理、轻量工作流
- 快速组合 task/entrypoint，而不显式构建 StateGraph

### 关键概念
- `task`：可并行的小任务
- `entrypoint`：工作流入口
- 可选 `checkpointer` 与 `cache` 提高可靠性与成本效率

```ts
import { task, entrypoint } from "@langchain/langgraph";

const fetchDoc = task("fetchDoc", async (id: string) => ({ id, text: "..." }));

const workflow = entrypoint("summarize", async (ids: string[]) => {
  const docs = await Promise.all(ids.map((id) => fetchDoc(id)));
  return docs.map((doc) => doc.text).join("\n");
});
```

---

## Graph API vs Functional API 选择指南

| 维度 | Graph API | Functional API |
| --- | --- | --- |
| 状态建模 | 强 | 中 |
| 复杂路由 | 强 | 弱 |
| 并发任务 | 中 | 强 |
| 可视化与调试 | 强 | 中 |
| 上手速度 | 中 | 快 |

建议：复杂流程优先 Graph API；多任务并发或批处理优先 Functional API。

---

## 阶段 9：生产级架构与工程实践

### 关注重点
- **应用结构**：拆分 graph、node、tools、prompts、infra
- **测试策略**：节点单测、图级集成测试、回归用例
- **可观测性**：LangSmith tracing、运行成本与质量指标
- **部署与运维**：LangGraph CLI、本地/服务端运行、版本升级

---

## 架构设计建议（实践版）

### 1. 分层与职责
- **Graph 层**：纯编排，不写外部 I/O
- **Node 层**：单一职责，尽量幂等
- **Tool/Adapter 层**：与外部系统对接
- **State 层**：只保存原始结构化数据

### 2. 状态设计
- 使用 reducer 让状态更新可预测（如 MessagesValue, ReducedValue）
- 避免把提示词拼接后的长文本写入状态
- 只存可恢复与可追踪的数据

### 3. 流程设计
- 明确 Start/End 节点
- 长流程要有可中断点（审批/人工反馈）
- 将“路由逻辑”放在专用节点，避免杂糅

### 4. 可观测与可靠性
- 给关键节点添加日志与 trace context
- 统一错误处理策略：可恢复 vs 不可恢复
- 使用 retry/caching（功能 API 支持）降低波动

---

## 项目最佳实践（工程化）

### 推荐目录结构

```text
src/
  graphs/          # Graph 定义
  nodes/           # Node 实现
  tools/           # Tool 封装
  prompts/         # Prompt 模板
  state/           # State schema
  infra/           # 数据库/搜索/第三方服务
  server/          # API/CLI 封装
  evals/           # 评测与回归用例
```

### 配置与安全
- 使用 `.env` 管理密钥，避免硬编码
- 给工具调用加权限与审计
- 对外部依赖增加超时与熔断

### 测试策略
- Node 单测：用 mock 模型和伪数据验证逻辑
- Graph 集成：验证路由、分支与最终输出
- 回归测试：用固定输入保证行为一致性

---

## 进阶项目建议（从练手到专家）

1. **多渠道客服代理**：邮件/工单/聊天多入口，统一路由与升级。
2. **RAG+任务型智能体**：检索后多步推理与行动链。
3. **企业流程自动化**：审批、合规、人审与自动执行闭环。

---

## 官方文档索引（TypeScript）

- Overview: https://docs.langchain.com/oss/javascript/langgraph/overview
- Install: https://docs.langchain.com/oss/javascript/langgraph/install
- Quickstart: https://docs.langchain.com/oss/javascript/langgraph/quickstart
- Thinking in LangGraph: https://docs.langchain.com/oss/javascript/langgraph/thinking-in-langgraph
- Workflows + Agents: https://docs.langchain.com/oss/javascript/langgraph/workflows-agents
- Persistence: https://docs.langchain.com/oss/javascript/langgraph/persistence
- Durable Execution: https://docs.langchain.com/oss/javascript/langgraph/durable-execution
- Streaming: https://docs.langchain.com/oss/javascript/langgraph/streaming
- Interrupts: https://docs.langchain.com/oss/javascript/langgraph/interrupts
- Time Travel: https://docs.langchain.com/oss/javascript/langgraph/use-time-travel
- Memory: https://docs.langchain.com/oss/javascript/langgraph/add-memory
- Subgraphs: https://docs.langchain.com/oss/javascript/langgraph/use-subgraphs
- Application Structure: https://docs.langchain.com/oss/javascript/langgraph/application-structure
- Test: https://docs.langchain.com/oss/javascript/langgraph/test
- Studio: https://docs.langchain.com/oss/javascript/langgraph/studio
- Agent Chat UI: https://docs.langchain.com/oss/javascript/langgraph/ui
- Deploy: https://docs.langchain.com/oss/javascript/langgraph/deploy
- Observability: https://docs.langchain.com/oss/javascript/langgraph/observability
- Runtime (Pregel): https://docs.langchain.com/oss/javascript/langgraph/pregel
- Changelog: https://docs.langchain.com/oss/javascript/releases/changelog
- API Reference: https://reference.langchain.com/javascript

# TypeScript 示例

使用 pnpm + tsx 管理环境和运行的 LangChain TypeScript 示例集合。

## 快速开始

### 1. 安装 pnpm

```bash
npm install -g pnpm
```

### 2. 安装依赖

```bash
cd langchain-typescript
pnpm install
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥
```

### 4. 验证环境

```bash
pnpm check-env
```

### 5. 运行示例

```bash
# 基础链
pnpm 01-hello-chain

# 提示词模板
pnpm 02-prompt-template

# 带记忆的对话
pnpm 03-memory-chat

# 检索增强问答
pnpm 04-rag-qa

# 天气智能体
pnpm 05-agent-weather

# API 服务
pnpm 06-api-deployment

# Agent Chat 基础版
pnpm 12-agent-chat

# Agent Chat 完整版
pnpm 13-agent-complete
```

### 语法

旧用法:
- 直接调用 llm.invoke()
- 需要手动管理消息格式

新用法 LCEL:
- 使用 .pipe() 链式调用
- 自动处理消息格式
- 支持流式输出、批处理、异步

## 可用命令

```bash
# 开发模式（监听文件变化）
pnpm dev

# 构建项目
pnpm build

# 类型检查
pnpm check

# 代码检查
pnpm lint

# 代码格式化
pnpm format
```

## 目录结构

```
langchain-typescript/
├── src/
│   ├── 01-hello-chain.ts       # 基础链 (LCEL)
│   ├── 02-prompt-template.ts   # 提示词模板 (LCEL)
│   ├── 03-memory-chat.ts       # 带记忆的对话 (LCEL)
│   ├── 04-rag-qa.ts            # 检索增强问答 (LCEL)
│   ├── 05-agent-weather.ts     # 天气智能体
│   ├── 06-api-deployment.ts    # API 部署
│   ├── 07-advanced-agents.ts   # 高级智能体
│   ├── 08-structured-output.ts # 结构化输出
│   ├── 09-multi-agent/         # 多智能体协作系统
│   │   ├── index.ts            # 主入口
│   │   ├── types.ts            # 类型定义
│   │   ├── base-agent.ts       # 基础 Agent 类
│   │   ├── researcher-agent.ts # 研究员 Agent
│   │   ├── coder-agent.ts      # 编码 Agent
│   │   ├── reviewer-agent.ts   # 审查 Agent
│   │   └── supervisor-agent.ts # 监督 Agent
│   ├── 10-streaming-chat/      # 流式聊天应用
│   ├── 11-production-tracing.ts # 生产环境追踪
│   ├── 12-agent-chat/          # Agent Chat 基础版
│   ├── 13-agent-complete/      # Agent Chat 完整版
│   ├── clients/                # 客户端工具
│   │   ├── model.ts
│   │   ├── embedding.ts
│   │   ├── agent.ts
│   │   ├── tavily.ts
│   │   └── rag-text.ts
│   └── check-env.ts            # 环境验证
├── package.json                # 项目配置
├── tsconfig.json               # TypeScript 配置
└── .env.example                # 环境变量模板
```

## 实现说明

### LCEL (LangChain Expression Language)

TypeScript 版本的 LCEL 使用 `.pipe()` 方法链式调用：

```typescript
// LCEL 示例
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

const prompt = ChatPromptTemplate.fromTemplate("问题：{question}");
const chain = prompt.pipe(llm).pipe(new StringOutputParser());
const result = await chain.invoke({ question: "什么是 LangChain？" });
```

### Agent 实现

TypeScript 版本目前使用 `createReactAgent`（LangChain 传统方式）：

```typescript
import { createReactAgent, AgentExecutor } from "langchain/agents";

const agent = await createReactAgent({ llm, tools, prompt });
const agentExecutor = new AgentExecutor({ agent, tools, verbose: true });
const result = await agentExecutor.invoke({ input: "..." });
```

**注意**: TypeScript 版本的 `create_agent` API 尚未完全稳定，建议使用 `createReactAgent` 作为替代方案。

## 技术栈

- **运行时**: Node.js ≥ 18
- **包管理器**: pnpm
- **执行器**: tsx
- **框架**: LangChain TypeScript
- **类型检查**: TypeScript
- **代码风格**: ESLint + Prettier

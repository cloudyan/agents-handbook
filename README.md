# 🦜🔗 Agents Handbook（Python & TypeScript）

「一份多框架 AI Agent 开发实战手册，涵盖 LangChain、ai-sdk、claude-agent-sdk 等主流框架，帮助你用最短时间掌握大模型应用开发。」

---

## 📌 项目定位
- 覆盖多个主流 AI 开发框架：LangChain、ai-sdk、claude-agent-sdk
- 一份代码，两份体验：同场景分别给出 Python 与 TypeScript 实现
- 从「Hello Chain」→「可部署智能体」逐步递进，每个示例均可在笔记本或容器里一键跑通
- 统一环境、统一配置、统一提示词，方便横向对比不同框架和语言的差异
- **支持 LangChain 1.0 新 API**：提供新旧两种实现方式，方便学习和迁移

---

## 🆕 LangChain 1.0 更新

LangChain 1.0 引入了全新的 Agent 框架，本项目同时提供新旧两种实现：

### 主要变化

| 维度 | 旧版 API | 新版 API (LangChain 1.0) |
|------|---------|-------------------------|
| **创建方式** | 多个分支函数 (`create_tool_calling_agent`, `create_react_agent` 等) | 统一的 `create_agent()` |
| **底层架构** | LangChain 传统执行器 | LangGraph 状态图 |
| **消息格式** | `{"input": "...", "agent_scratchpad": ...}` | `{"messages": [{"role": "user", "content": "..."}]}` |
| **记忆管理** | 手动管理 (`BufferWindowMemory` 等) | 内置 `checkpointer` 机制 |
| **代码量** | 较多 | 减少 40%+ |

### 代码对比

```python
# ❌ 旧版
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个天气助手..."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "查询北京天气"})

# ✅ 新版 (LangChain 1.0)
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个天气助手..."
)
result = agent.invoke({"messages": [{"role": "user", "content": "查询北京天气"}]})
```

### 使用建议

- **学习 Agent 原理**： (`agent_weather.py`, `advanced_agents.py`)
- **多 Agent 系统**：基于 LangGraph，功能更强大 (`multi_agent_system.py`)

---

## 大模型

大模型使用兼容 openai 的国内大模型，环境变量需要配置

参见 .env.example 文件

```bash
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_BASE_URL=https://api.openai.com/v1
# MODEL_NAME=gpt-3.5-turbo
# PORT=4001
```

## 🧱 技术栈

| 类别 | LangChain Python | LangChain TypeScript | ai-sdk | claude-agent-sdk |
|---|---|---|---|---|
| 环境管理 | uv | nvm + pnpm + tsx | pnpm | pnpm |
| 依赖文件 | pyproject.toml | package.json | package.json | package.json |
| 交互开发 | Jupyter Lab | VSCode 调试 | VSCode 调试 | VSCode 调试 |
| 主框架 | langchain | langchain | ai-sdk | claude-agent-sdk |
| LLM 调用 | openai、langchain-openai | openai、langchain-openai | openai | anthropic |
| 向量库 | Chroma、FAISS | chromadb | - | - |
| 部署 | FastAPI + Uvicorn | Express + tsx | Next.js | Next.js |
| 代码风格 | black / ruff | prettier / eslint | prettier / eslint | prettier / eslint |int |


- Python 环境管理 [uv](https://github.com/astral-sh/uv)
- Python 交互式开发环境 [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
- 大模型应用开发框架 [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- AI 开发工具包 [ai-sdk](https://sdk.vercel.ai/)
- Claude Agent SDK [claude-agent-sdk](https://github.com/anthropics/claude-agent-sdk)
- [OpenAI Python SDK](https://github.com/openai/openai-python?tab=readme-ov-file#installation)

---

## 🗂️ 目录结构

```bash
agents-handbook/
  ├─ langchain-python/       # LangChain Python 示例
  │  ├─ 00-env/              # 环境自检
  │  ├─ 01-hello-chain/      # 最简 LLMChain
  │  ├─ ...
  │  └─ pyproject.toml
  ├─ langchain-typescript/   # LangChain TypeScript 示例
  │  ├─ src/
  │  │  ├─ 01-hello-chain.ts
  │  │  └─ ...
  │  └─ package.json
  ├─ ai-sdk/                 # ai-sdk 示例（待添加）
  ├─ claude-agent-sdk/       # claude-agent-sdk 示例（待添加）
  ├─ .env.example           # 环境变量模板
  └─ README.md
```

---

## 🚀 一键启动

### LangChain Python 使用 uv
```bash
# 1. 创建并激活虚拟环境
cd langchain-python
uv venv --python 3.11
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 2. 安装依赖
uv sync

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥

# 4. 验证环境
python 00-env/simple_check.py

# 5. 运行示例
python 05-agent-weather/agent_weather.py
python 07-advanced-agents/advanced_agents.py
python 09-multi-agent/multi_agent_system.py

# 或使用 Jupyter Lab
jupyter lab 01-hello-chain/
```

### LangChain TypeScript 使用 pnpm + tsx
```bash
# 1. 进入目录并安装依赖
cd langchain-typescript
pnpm install

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥

# 3. 验证环境
pnpm check-env

# 4. 运行示例
pnpm 01-hello-chain
pnpm 05-agent-weather

# 5. 运行 API 服务
pnpm 06-api-deployment

# 6. 运行 Agent Chat 服务（示例 12）
pnpm 12-agent-chat

# 7. 运行完整版 Agent Chat 服务（示例 13）
pnpm 13-agent-complete
```

---

## 📑 完整示例清单

### 基础入门（01-03）

| 编号 | 示例 | 关键词 | 难度 | Python | TS | 说明 |
|---|---|---|---|---|---|---|
| 01 | Hello Chain | LLMChain | ⭐ | ✅ | ✅ | 最小可运行链，理解 Chain 概念 |
| 02 | Prompt Template | 模板渲染 | ⭐ | ✅ | ✅ | System/Human 模板，变量注入 |
| 03 | Memory Chat | BufferWindowMemory | ⭐⭐ | ✅ | ✅ | 多轮对话记忆管理 |

### 核心应用（04-06）

| 编号 | 示例 | 关键词 | 难度 | Python | TS | 说明 |
|---|---|---|---|---|---|---|
| 04 | RAG QA | WebBaseLoader + Chroma | ⭐⭐ | ✅ | ✅ | 文档切片→向量→检索问答 |
| 05 | 获取天气智能体 | OpenAI Functions + Tool | ⭐⭐⭐ | ✅ | ✅ | Agent 调用外部 API |
| 06 | API 部署 | FastAPI/Express | ⭐⭐⭐ | ✅ | ✅ | 封装为 HTTP 服务 |

### 进阶实战（07-11）

| 编号 | 示例 | 关键词 | 难度 | Python | TS | 说明 |
|---|---|---|---|---|---|---|
| 07 | 高级 Agent 模式 | ReAct / Self-Ask / Plan-Execute | ⭐⭐⭐ | ✅ | ✅ | 不同 Agent 开发模式对比 |
| 08 | 结构化输出 | Pydantic / Zod | ⭐⭐⭐ | ✅ | ✅ | 强类型数据提取与验证 |
| 09 | 多智能体协作 | Supervisor + Sub-agents | ⭐⭐⭐⭐⭐ | ✅ | ✅ | 任务分解与协作 |
| 10 | 流式输出 + ChatUI | Streaming + WebSocket | ⭐⭐⭐⭐ | ✅ | ⏳ | 实时响应前端交互 |
| 11 | 生产级追踪 | LangSmith + 日志 | ⭐⭐⭐⭐⭐ | ✅ | ✅ | 监控、调试、优化 |
| 12 | Agent Chat 基础版 | LangGraph CLI + UI 对接 | ⭐⭐⭐ | ✅ | ✅ | 基础对话功能，LangGraph CLI 集成演示 |
| 13 | Agent Chat 完整版 | ReAct + Tools + Streaming | ⭐⭐⭐⭐⭐ | ✅ | ✅ | 完整 Agent 能力，工具调用、多轮对话、复杂推理 |

### 学习路径

- **初学者**：01 → 02 → 03 → 04
- **进阶开发者**：05 → 06 → 07 → 08
- **高级工程师**：09 → 10 → 11 → 12

---

## 🔑 环境变量配置

所有示例优先读取项目根目录的 `.env` 文件：

```bash
# DeepSeek API Key - 用于大模型调用
# 获取地址：https://platform.deepseek.com/
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Tavily Search API Key - 用于网络搜索功能
# 获取地址：https://www.tavily.com/
TAVILY_API_KEY=your_tavily_api_key_here

# OpenWeather API Key - 用于天气查询功能
# 获取地址：https://home.openweathermap.org/
OPENWEATHER_API_KEY=your_openweather_api_key_here

# 可选：自定义 OpenAI Base URL
OPENAI_BASE_URL=https://api.deepseek.com/v1
```

---

## 🧪 05 获取天气智能体（运行效果）
**输入**：「明天我需要带伞吗？」
**输出**：

```md
Thought: 需要查询用户所在地的天气
Action: get_weather
Action Input: {"location": "Beijing", "days": 1}
Observation: {"rain": true, "temp": 18}
Final Answer: 明天北京有小雨，建议带伞☔，气温约 18℃。
```

---

## 📈 路线图
- [x] 07 高级 Agent 模式（ReAct / Self-Ask / Plan-Execute）
- [x] 08 结构化输出（Pydantic / Zod）
- [x] 09 多智能体协作（Supervisor 模式）
- [x] 10 流式输出 + 前端 ChatUI
- [x] 11 生产级日志、追踪（LangSmith）
- [x] 12 完整聊天服务（Agent + SSE + Session + Analytics）

---

## 🤝 贡献指南
1. Fork → 新建 `feat/xxx` 分支
2. 确保 `pnpm lint` & `pnpm test` 通过
3. 提交 PR，并勾选「允许维护者编辑」

# Python 示例

使用 uv 管理环境和依赖的 LangChain Python 示例集合。

## 快速开始

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 使用 pip 安装
pip install uv
```

### 2. 创建虚拟环境

```bash
cd langchain-python
uv venv --python 3.11
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥
```

### 5. 验证环境

```bash
python 00-env/simple_check.py
```

### 6. 运行示例

```bash
# 使用 Jupyter Lab
jupyter lab 01-hello-chain/

# 直接运行 Python 文件
python 01-hello-chain/hello_chain.py
python 05-agent-weather/agent_weather.py

# 运行 API 服务
python 06-api-deployment/main.py
```

## 开发工具

```bash
# 代码格式化
uv run black .
uv run ruff check --fix .

# 类型检查
uv run mypy .

# 运行测试
uv run pytest
```

## 目录结构

```
python/
├── 00-env/              # 环境验证
├── 01-hello-chain/      # 基础链
├── 02-prompt-template/  # 提示词模板
├── 03-memory-chat/      # 带记忆的对话
├── 04-rag-qa/           # 检索增强问答
├── 05-agent-weather/    # 天气智能体 🆕 v2 (LangChain 1.0)
├── 06-api-deployment/   # API 部署
├── 07-advanced-agents/  # 高级智能体 🆕 v2 (LangChain 1.0)
├── 08-structured-output/ # 结构化输出
├── 09-multi-agent/      # 多智能体协作 🆕 v2 (LangChain 1.0)
├── 10-streaming-chat/   # 流式输出 + ChatUI
├── 11-production-tracing/ # 生产级追踪
├── pyproject.toml       # 项目配置
└── requirements.txt     # 依赖列表
```

## LangChain 版本说明

本项目提供两种 Agent 实现方式：

### 旧版 API (传统方式)
- 使用 `create_tool_calling_agent`、`create_react_agent` 等分支函数
- 需要手动配置 `AgentExecutor`、`ChatPromptTemplate`
- 适合学习 Agent 原理和底层机制
- 文件：`agent_weather.py`、`advanced_agents.py`、`multi_agent_system.py`

### 新版 API (LangChain 1.0)
- 使用统一的 `create_agent` API
- 基于 LangGraph 底层架构
- 内置记忆管理、自动 ReAct 循环
- 更简洁，适合生产环境
- 文件：`agent_weather_v2.py`、`advanced_agents_v2.py`、`multi_agent_system_v2.py`

### 快速对比

```python
# ❌ 旧版
prompt = ChatPromptTemplate.from_messages([...])
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
result = executor.invoke({"input": "..."})

# ✅ 新版
agent = create_agent(model=llm, tools=tools, system_prompt="...")
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

### 运行新版本示例

```bash
# Agent Weather (LangChain 1.0)
python 05-agent-weather/agent_weather_v2.py

# Advanced Agents (LangChain 1.0)
python 07-advanced-agents/advanced_agents_v2.py

# Multi-Agent System (LangChain 1.0)
python 09-multi-agent/multi_agent_system_v2.py
```

**注意**：新版本示例需要安装 `langgraph`：
```bash
uv add langgraph
```

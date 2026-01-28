# 🦜🔗 LangChain Python 示例

LangChain Python 实战示例，涵盖从基础到高级的所有功能。

## 📁 项目结构

```
langchain-python/
├── 00-env/                    # 环境自检
├── 01-hello-chain/            # 最简 LLMChain
├── 02-prompt-template/        # 提示词模板
├── 03-memory-chat/            # 记忆聊天
├── 04-rag-qa/                 # RAG 问答系统
├── 05-agent-weather/          # 天气智能体
├── 06-api-deployment/         # API 部署
├── 07-advanced-agents/        # 高级智能体
├── 08-structured-output/      # 结构化输出
├── 09-multi-agent/            # 多智能体系统
├── 10-streaming-chat/         # 流式聊天
├── 11-production-tracing/     # 生产级追踪
├── clients/                   # 公共客户端模块
├── utils/                     # 公共工具模块
├── test_all_examples.py       # 测试脚本
├── generate_notebooks.py      # 生成 Notebook 脚本
└── REFACTORING_SUMMARY.md     # 重构总结
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd langchain-python
uv sync
```

### 2. 配置环境变量

复制 `.env.example` 为 `.env` 并配置 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
```

### 3. 运行示例

#### 运行 Python 脚本

```bash
# 基础示例
uv run python 04-rag-qa/rag_qa.py
uv run python 05-agent-weather/agent_weather.py

# 启动服务
uv run python 06-api-deployment/main.py
uv run python 10-streaming-chat/chat_server.py
```

#### 运行 Jupyter Notebook

```bash
# 启动 Jupyter Lab
jupyter lab

# 或使用 uv
uv run jupyter lab
```

在 Jupyter Lab 中打开对应的 `.ipynb` 文件查看文档说明。

⚠️ **重要说明**：
- Jupyter Notebook 主要用于查看文档和说明
- 完整的可执行代码在 Python 脚本中
- 建议使用 Python 脚本运行示例

### 4. 运行测试

```bash
# 测试所有示例
uv run python test_all_examples.py

# 重新生成所有 Notebook（仅包含文档说明）
uv run python create_simple_notebooks.py
```

## 📚 示例说明

### 基础入门（01-03）

| 编号 | 示例 | 关键词 | 难度 |
|---|---|---|---|
| 01 | Hello Chain | LLMChain | ⭐ |
| 02 | Prompt Template | 模板渲染 | ⭐ |
| 03 | Memory Chat | BufferWindowMemory | ⭐⭐ |

### 核心应用（04-06）

| 编号 | 示例 | 关键词 | 难度 |
|---|---|---|---|
| 04 | RAG QA | Chroma + 向量检索 | ⭐⭐ |
| 05 | 天气智能体 | Tool + Agent | ⭐⭐⭐ |
| 06 | API 部署 | FastAPI | ⭐⭐⭐ |

### 进阶实战（07-11）

| 编号 | 示例 | 关键词 | 难度 |
|---|---|---|---|
| 07 | 高级 Agent | ReAct / Plan-Execute | ⭐⭐⭐ |
| 08 | 结构化输出 | Pydantic | ⭐⭐⭐ |
| 09 | 多智能体 | Supervisor 模式 | ⭐⭐⭐⭐⭐ |
| 10 | 流式聊天 | WebSocket | ⭐⭐⭐⭐ |
| 11 | 生产追踪 | LangSmith | ⭐⭐⭐⭐⭐ |

## 🎯 学习路径

### 初学者
1. 01-hello-chain → 02-prompt-template → 03-memory-chat
2. 理解 Chain、Prompt 和 Memory 的基本概念

### 进阶开发者
1. 04-rag-qa → 05-agent-weather → 06-api-deployment
2. 学习 RAG、Agent 和 API 部署

### 高级工程师
1. 07-advanced-agents → 08-structured-output → 09-multi-agent
2. 10-streaming-chat → 11-production-tracing
3. 掌握高级模式和最佳实践

## 🔧 公共模块

### clients/

#### model_client.py
```python
from clients import create_model_client

llm = create_model_client(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    streaming=False
)
```

#### embedding_client.py
```python
from clients import create_embedding_client

embeddings = create_embedding_client(
    model_name="text-embedding-ada-002",
    use_fake=False  # 是否使用 FakeEmbeddings
)
```

#### tavily_client.py
```python
from clients import create_search_tool

search_tool = create_search_tool()
```

### utils/

#### monitor.py
```python
from utils import PerformanceMonitor, CustomCallbackHandler, setup_langsmith

monitor = PerformanceMonitor()
monitor.start_tracking()
# ... 执行代码 ...
metrics = monitor.end_tracking("chain_name", True)
```

## ⚠️ 重要说明

### API 兼容性

某些 API（如 DeepSeek）可能不支持 embeddings 端点。代码会自动使用 FakeEmbeddings 作为替代。

### LangChain 1.0 API

推荐使用 LangChain 1.0 新 API：

```python
# 新版 API（推荐）
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=[tool],
    system_prompt="你是一个智能助手"
)
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]})
```

### 环境变量

确保配置以下环境变量：

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_base_url
MODEL_NAME=your_model_name
```

## 📝 代码规范

- 所有注释使用中文
- 使用公共模块减少重复代码
- 完整的错误处理和日志记录
- Python 版本：3.11+

## 🧪 测试

```bash
# 运行所有测试
uv run python test_all_examples.py

# 测试单个示例
uv run python 04-rag-qa/rag_qa.py
```

## 🔄 与 TypeScript 版本对齐

Python 版本与 TypeScript 版本保持一致：
- 相同的公共模块结构
- 相同的 API 设计
- 相同的功能特性

## 📚 相关文档

- [LangChain 官方文档](https://python.langchain.com/)
- [LangChain 1.0 升级指南](https://python.langchain.com/docs/versions/migrating_chains/)
- [REFACTORING_SUMMARY.md](./REFACTORING_SUMMARY.md) - 详细重构总结

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

# 09 - 多智能体协作系统

基于 LangGraph 的多智能体协作系统，实现任务分配和协同工作。

## 功能特性

- **多 Agent 协作**: Researcher、Coder、Reviewer 三个专业 Agent 协同工作
- **智能任务分配**: Supervisor 根据任务类型自动分配给合适的 Agent
- **可视化调试**: 使用 LangGraph CLI 提供图形化界面
- **状态管理**: 基于 LangGraph 的状态流转机制

## 快速开始

### 1. 安装依赖

```bash
cd langchain-python
uv sync
```

**重要**：LangGraph CLI 需要额外的依赖包，已在 `pyproject.toml` 中配置为 `langgraph-cli[inmem]`，会自动安装：
- `langgraph-api`: LangGraph API 服务器
- `langgraph-runtime-inmem`: 内存运行时

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 OPENAI_API_KEY
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 OPENAI_API_KEY
```

### 3. 运行方式

#### 方式 1: 命令行运行（推荐）

```bash
uv run python 09-multi-agent/index.py
```

或者：

```bash
cd 09-multi-agent && uv run python index.py
```

#### 方式 2: LangGraph Web UI

```bash
cd langchain-python
source .venv/bin/activate

uv run langgraph dev --config ./09-multi-agent/langgraph.json
```

访问 http://localhost:8123，在浏览器中输入任务进行测试。

**注意**：Python 版本现在也支持 LangGraph CLI，与 TypeScript 版本功能完全对齐！

## 项目结构

```
09-multi-agent/
├── agents/
│   ├── __init__.py          # 模块初始化
│   ├── base_agent.py        # 基础 Agent 类
│   ├── supervisor_agent.py  # 监督 Agent（任务分配）
│   ├── researcher_agent.py  # 研究员 Agent（信息搜集）
│   ├── coder_agent.py       # 编码 Agent（代码实现）
│   └── reviewer_agent.py    # 审查 Agent（代码审查）
├── __init__.py              # 模块初始化
├── clients/
│   └── __init__.py          # 客户端工具（模型、搜索）
├── graph.py                 # LangGraph 工作流定义
├── index.py                 # 命令行入口
├── langgraph.json           # LangGraph 配置
└── multi_agent_system.py    # 旧版单文件实现（已废弃）
```

## 工作流程

```
用户输入任务
    ↓
Supervisor（任务分析）
    ↓
Researcher（技术调研）
    ↓
    ├─→ Coder（代码实现）
    │       ↓
    │   Reviewer（代码审查）
    │       ↓
    └────────┘
            ↓
        汇总结果
```

## Agent 说明

### Supervisor
- 分析任务类型（代码开发/研究/通用）
- 协调各 Agent 的工作流程

### Researcher
- 使用搜索工具搜集信息
- 生成技术研究报告

### Coder
- 根据研究报告编写代码
- 遵循最佳实践和代码规范

### Reviewer
- 检查代码质量和性能
- 提供改进建议

## 运行示例

在 Web UI 或命令行中输入以下任务：

- 代码开发: "实现一个快速排序算法，使用 Python 实现"
- 研究任务: "研究 Python 的最佳实践"
- 通用任务: "解释什么是机器学习"

## 技术栈

- **LangGraph**: 工作流编排
- **LangChain**: LLM 和工具集成
- **Python**: 类型安全
- **Asyncio**: 异步编程

## 相关文档

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)

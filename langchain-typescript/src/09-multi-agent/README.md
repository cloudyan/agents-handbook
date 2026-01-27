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
cd langchain-typescript
pnpm install
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置 OPENAI_API_KEY 和 TAVILY_API_KEY
```

### 3. 运行方式

#### 方式 1: LangGraph Web UI（推荐）

```bash
pnpm 09-multi-agent:dev
```

访问 http://localhost:8123，在浏览器中输入任务进行测试。

#### 方式 2: 命令行运行

```bash
pnpm 09-multi-agent
```

**注意**：TypeScript 和 Python 版本现在都支持 LangGraph CLI，功能完全对齐。两种版本都提供 CLI 和 Web UI 两种运行方式。

## 项目结构

```
09-multi-agent/
├── agents/
│   ├── base-agent.ts        # 基础 Agent 类
│   ├── supervisor-agent.ts  # 监督 Agent（任务分配）
│   ├── researcher-agent.ts  # 研究员 Agent（信息搜集）
│   ├── coder-agent.ts       # 编码 Agent（代码实现）
│   └── reviewer-agent.ts    # 审查 Agent（代码审查）
├── graph.ts                 # LangGraph 工作流定义
├── index.ts                 # 命令行入口
├── langgraph.json           # LangGraph 配置
└── types.ts                 # 类型定义
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

- 代码开发: "实现一个快速排序算法，使用 JS 实现"
- 研究任务: "研究 Python 的最佳实践"
- 通用任务: "解释什么是机器学习"

## 技术栈

- **LangGraph**: 工作流编排
- **LangChain**: LLM 和工具集成
- **Tavily Search**: 搜索工具
- **TypeScript**: 类型安全

## 相关文档

- [LangGraph CLI 使用指南](./README-langgraph.md)
- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)

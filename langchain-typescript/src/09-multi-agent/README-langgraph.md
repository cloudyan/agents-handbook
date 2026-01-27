# 使用 LangGraph CLI 开发多智能体系统

## 快速开始

### 1. 安装依赖

```bash
cd langchain-typescript
pnpm install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置 API Key
# OPENAI_API_KEY=your_api_key
# OPENAI_BASE_URL=your_base_url
```

### 3. 启动 LangGraph 开发服务器

```bash
# 方式 1：使用 npm 脚本（推荐）
cd langchain-typescript
pnpm 09-multi-agent:dev

# 方式 2：直接使用 npx
cd langchain-typescript
npx @langchain/langgraph-cli dev --config src/09-multi-agent/langgraph.json
```

### 4. 访问 Web UI

打开浏览器访问：`http://localhost:8123`

## 功能特性

### 可视化 Graph 结构
- 查看多智能体协作流程
- 实时显示节点执行状态
- 查看状态流转路径

### 交互式测试
- 在浏览器中直接测试任务
- 查看每个 Agent 的输入输出
- 调试复杂的多步骤流程

### 实时调试
- 查看每一步的执行时间
- 检查中间状态
- 快速定位问题

## 使用方式

### 方式 1：使用 LangGraph CLI（推荐）

```bash
# 启动开发服务器
cd langchain-typescript
pnpm 09-multi-agent:dev

# 访问 http://localhost:8123
# 在浏览器中输入任务，例如：
# "实现一个快速排序算法，使用 JS 实现"
```

### 方式 2：直接运行

```bash
# 使用原始方式运行
cd langchain-typescript
pnpm 09-multi-agent
```

## Graph 结构

```
用户输入
    ↓
supervisor（任务分析）
    ↓
researcher（研究/调研）
    ↓
    ├─→ coder（代码实现）
    │       ↓
    │   reviewer（代码审查）
    │       ↓
    └────────┘
            ↓
        summary（结果汇总）
            ↓
        输出结果
```

## 节点说明

### supervisor
- 分析任务类型（代码开发/研究/通用）
- 决定下一步执行哪个 Agent

### researcher
- 进行技术调研
- 查找相关资料
- 生成研究报告

### coder
- 根据研究报告编写代码
- 实现具体功能

### reviewer
- 审查代码质量
- 提供改进建议

### summary
- 汇总所有 Agent 的结果
- 生成最终报告

## 配置文件

### langgraph.json

```json
{
  "graphs": {
    "multi-agent": "./graph.ts"
  },
  "env": ".env"
}
```

- `graphs`: 定义 Graph 的入口文件
- `env`: 环境变量文件路径

## 状态管理

```typescript
interface AgentState {
  messages: Array<{ role: string; content: string }>;
  task: string;
  researchReport?: string;
  codeContent?: string;
  reviewReport?: string;
  taskType?: string;
  nextNode?: string;
}
```

## 开发技巧

### 1. 热重载

修改代码后，LangGraph CLI 会自动重新加载，无需重启服务器。

### 2. 查看状态

在 Web UI 中可以实时查看每个节点的状态变化。

### 3. 调试模式

在启动命令中添加 `--debug` 参数：

```bash
pnpm 09-multi-agent:dev --debug
```

### 4. 测试不同任务

在 Web UI 中输入不同类型的任务，观察不同的执行路径：
- 代码开发任务：触发 researcher → coder → reviewer 流程
- 研究任务：触发 researcher → summary 流程
- 通用任务：触发 researcher → summary 流程

## 常见问题

### Q: 端口被占用怎么办？

A: 修改启动命令指定端口：

```bash
npx @langchain/langgraph-cli dev --config src/09-multi-agent/langgraph.json --port 8124
```

### Q: 如何查看详细日志？

A: 在启动命令中添加 `--debug` 参数：

```bash
pnpm 09-multi-agent:dev --debug
```

### Q: Graph 流程不按预期执行？

A: 检查 `graph.ts` 中的条件边逻辑，确保返回值正确。

## 与原始版本的区别

| 特性 | 原始版本 | LangGraph CLI 版本 |
|------|---------|-------------------|
| 界面 | 命令行 | Web UI |
| 调试 | 日志输出 | 可视化调试 |
| 测试 | 修改代码 | 交互式测试 |
| 状态追踪 | 手动 | 自动可视化 |
| 适用场景 | 生产环境 | 开发调试 |

## 下一步

1. 尝试不同的任务类型
2. 添加新的 Agent 节点
3. 修改 Graph 流程逻辑
4. 集成 LangSmith 追踪

## 相关资源

- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [LangSmith 文档](https://docs.smith.langchain.com/)
- [示例代码](./index.ts)

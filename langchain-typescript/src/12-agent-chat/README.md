# Agent Chat 基础版 - LangGraph CLI 集成指南

本示例展示如何将 LangChain 服务与 [Agent Chat UI](https://agentchat.vercel.app/) 对接，实现基础对话功能。

## 🎯 版本说明

- **12-agent-chat（当前）**：基础版，适合学习 LangGraph CLI 和 UI 对接
- **13-agent-complete**：完整版，具备工具调用、多轮对话、复杂推理等完整功能

## 📊 功能对比

| 功能 | 12 基础版 | 13 完整版 |
|------|----------|----------|
| 基础对话 | ✅ | ✅ |
| 工具调用 | ⚠️ 1 个工具 | ✅ 4 个工具 |
| 多轮对话 | ⚠️ 基础 | ✅ 完整 |
| ReAct 推理 | ❌ | ✅ |
| 流式输出 | ⚠️ API 支持 | ✅ 已启用 |
| 错误处理 | ⚠️ 基础 | ✅ 完善 |

## 🎯 使用 LangGraph CLI

### 快速开始

#### 1. 启动后端服务

```bash
cd langchain-typescript
pnpm 12-agent-chat
```

服务将在 `http://localhost:2024` 启动，自动提供完整的 LangGraph API。

#### 2. 获取 Assistant ID

服务启动后，访问以下 URL 获取 Assistant ID：

```bash
curl -X POST http://localhost:2024/assistants/search \
  -H "Content-Type: application/json" \
  -d '{"query": ""}'
```

返回的 `assistant_id` 就是你的 Assistant ID。

#### 3. 配置前端

创建 `agent-chat-ui/.env.local` 文件：

```bash
NEXT_PUBLIC_API_URL=http://localhost:2024
NEXT_PUBLIC_ASSISTANT_ID=<你的 Assistant ID>
```

#### 4. 启动前端界面

```bash
cd agent-chat-ui
pnpm dev
```

#### 5. 访问聊天界面

打开浏览器访问 `http://localhost:3000`，或直接使用线上服务：

```
https://agentchat.vercel.app/?apiUrl=http://localhost:2024&assistantId=<你的 Assistant ID>
```

## 📁 项目结构

```
src/12-agent-chat/
├── graph.ts           # LangGraph 图定义（核心逻辑）
├── langgraph.json     # LangGraph CLI 配置文件
├── test-api.ts        # API 测试脚本
└── index.ts           # 手动实现的 Express API（参考用）
```

## 🔧 LangGraph CLI 配置

### langgraph.json

```json
{
  "graphs": {
    "agent": "./graph.ts:app"
  },
  "env": "../../.env"
}
```

### graph.ts

定义你的 LangGraph 图，包括：
- 状态定义
- 节点函数
- 边和条件边
- 工具绑定

## 🌐 LangGraph CLI API 端点

LangGraph CLI 自动提供以下端点：

### Assistant 相关

- `POST /assistants/search` - 搜索 assistants
- `GET /assistants/{assistant_id}` - 获取 assistant 信息
- `GET /assistants/{assistant_id}/graph` - 获取图结构
- `GET /assistants/{assistant_id}/schemas` - 获取 schemas

### Thread 相关

- `POST /threads` - 创建新线程
- `GET /threads` - 获取线程列表
- `POST /assistants/{assistant_id}/threads` - 创建 assistant 的线程
- `GET /assistants/{assistant_id}/threads` - 获取 assistant 的线程

### Run 相关

- `POST /assistants/{assistant_id}/threads/{thread_id}/runs/stream` - 流式运行
- `GET /threads/{thread_id}/runs/{run_id}` - 获取运行状态

### 系统

- `GET /info` - 获取服务信息

## 🆚 两种方式对比

| 特性 | LangGraph CLI（推荐） | 手动实现（不推荐） |
|------|---------------------|-------------------|
| **代码量** | 极少（只需定义图） | 很多（需要实现所有端点） |
| **维护性** | 高（官方维护） | 低（需要自己维护） |
| **兼容性** | 完全兼容 LangGraph API | 可能不兼容 |
| **功能** | 完整（包括 Studio UI） | 有限 |
| **热重载** | ✅ 支持 | ❌ 不支持 |
| **推荐程度** | ⭐⭐⭐⭐⭐ | ⭐ |

## 🧪 测试 API

### 使用测试脚本

```bash
cd langchain-typescript
pnpm 12-test-api
```

### 手动测试

#### 获取 Assistant ID

```bash
curl -X POST http://localhost:2024/assistants/search \
  -H "Content-Type: application/json" \
  -d '{"query": ""}'
```

#### 创建线程

```bash
curl -X POST http://localhost:2024/threads \
  -H "Content-Type: application/json" \
  -d '{}'
```

#### 运行 Agent

```bash
curl -X POST http://localhost:2024/assistants/{assistant_id}/threads/{thread_id}/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {
          "role": "user",
          "content": "你好，请介绍一下你自己"
        }
      ]
    }
  }'
```

## 🛠️ 可用功能

当前 Agent 支持的功能：

1. **对话交互** - 多轮对话，上下文理解
2. **友好回复** - 中文自然语言回复
3. **可扩展** - 易于添加新工具和功能

## 🎨 Studio UI

LangGraph CLI 启动后，可以访问 Studio UI 进行可视化调试：

```
https://smith.langchain.com/studio?baseUrl=http://localhost:2024
```

在 Studio UI 中可以：
- 查看图结构
- 测试运行
- 查看状态变化
- 调试问题

## 🔍 故障排查

### 服务无法启动

1. 检查端口是否被占用：`lsof -ti:2024`
2. 检查依赖是否安装：`pnpm install`
3. 查看错误日志

### 前端无法连接

1. 确认后端服务正在运行
2. 检查 Assistant ID 是否正确
3. 查看 CORS 设置（LangGraph CLI 自动处理）

### Agent 返回空响应

1. 检查 `.env` 文件是否配置
2. 确认 `OPENAI_API_KEY` 是否有效
3. 确认 `OPENAI_BASE_URL` 和 `MODEL_NAME` 配置正确

## 📚 相关资源

- [Agent Chat UI](https://github.com/langchain-ai/agent-chat-ui)
- [Agent Chat UI Demo](https://agentchat.vercel.app)
- [LangGraph CLI 文档](https://langchain-ai.github.io/langgraph/how-tos/cli/)
- [LangGraph TypeScript](https://langchain-ai.github.io/langgraphjs/)

## 💡 最佳实践

1. **使用 LangGraph CLI** - 不要手动实现 API 服务
2. **定义清晰的图结构** - 使用 `StateGraph` 和 `Annotation`
3. **测试 Studio UI** - 利用可视化界面调试
4. **配置环境变量** - 在 `.env` 文件中管理密钥
5. **使用测试脚本** - 使用 `test-api.ts` 验证 API 功能

## 🎓 学习路径

1. **了解 LangGraph 基础** - 阅读 LangGraph 文档
2. **学习 Graph 定义** - 理解 `StateGraph`、节点、边
3. **测试 Studio UI** - 使用可视化界面
4. **集成 Agent Chat UI** - 连接前端界面
5. **扩展功能** - 添加工具和自定义节点

## 📦 环境变量配置

在项目根目录的 `.env` 文件中配置：

```bash
# DeepSeek API Key
OPENAI_API_KEY=your_deepseek_api_key_here

# API Base URL
OPENAI_BASE_URL=https://api.deepseek.com/v1

# 模型名称
MODEL_NAME=qwen3-max
```

## 🚀 快速命令

```bash
# 启动服务
pnpm 12-agent-chat

# 测试 API
pnpm 12-test-api

# 查看服务信息
curl http://localhost:2024/info
```

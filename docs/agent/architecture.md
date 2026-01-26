# 架构文档

本文档描述 Agents Handbook 项目的架构模式和设计原则。

## 项目结构哲学

### 双语言并行设计

项目采用 Python 和 TypeScript 双语言实现，每个示例都有对应的实现版本：

```
agents-handbook/
├── langchain-python/       # Python 实现
│   ├── 00-env/             # 环境验证
│   ├── 01-hello-chain/     # 基础示例
│   ├── ...
│   └── pyproject.toml
├── langchain-typescript/   # TypeScript 实现
│   ├── src/
│   │   ├── 01-hello-chain.ts
│   │   └── ...
│   └── package.json
```

**设计原则**：
- 相同的学习目标，不同的实现方式
- Python 侧重数据科学和快速原型
- TypeScript 侧重类型安全和生产部署

### 渐进式学习路径

示例按复杂度递增（⭐ 到 ⭐⭐⭐⭐⭐）：

1. **基础入门** (01-03)：理解核心概念
2. **核心应用** (04-06)：实际应用场景
3. **进阶实战** (07-11)：生产级特性

**学习曲线设计**：
- 每个示例独立完整，可单独运行
- 示例间有依赖关系，建议按顺序学习
- 每个示例包含 README 说明和代码注释

## 核心架构模式

### 1. 环境优先设计 (Environment-First)

所有示例都采用统一的环境配置模式：

```python
# Python 模式
from dotenv import load_dotenv
load_dotenv(override=True)

api_key = os.getenv("OPENAI_API_KEY", "")
```

```typescript
// TypeScript 模式
import dotenv from "dotenv";
dotenv.config({ override: true });

const apiKey = process.env.OPENAI_API_KEY;
```

**特点**：
- 统一的 `.env.example` 模板
- `override=True` 确保环境变量优先级
- 早期验证 API 密钥，快速失败

### 2. 模块化示例结构

每个示例目录包含：

```
XX-example-name/
├── README.md           # 学习目标和说明
├── example_name.py     # Python 脚本版本
├── example_name.ipynb  # Jupyter notebook 版本
└── (可选) requirements.txt  # 特定依赖
```

**设计原则**：
- 自包含，不依赖其他示例
- 双格式支持：脚本用于生产，notebook 用于学习
- 详细的 README 说明学习目标和关键概念

### 3. 错误处理模式

统一的错误处理和用户反馈：

```python
try:
    # LangChain 实现
    result = chain.invoke({"input": user_input})
    print("🎉 示例运行成功！")
    return 0
except Exception as e:
    print(f"运行错误：{e}")
    return 1
```

```typescript
try {
    const result = await chain.invoke({ input: userInput });
    console.log("✅ 示例运行完成！");
} catch (error) {
    console.error("运行错误：", error);
    process.exit(1);
}
```

**特点**：
- 中文错误消息
- 明确的退出码（0 成功，1 失败）
- 友好的用户反馈（使用 emoji）

### 4. LangChain 核心模式

#### LLMChain 模式 (基础)

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有帮助的助手"),
    ("user", "{input}")
])

chain = prompt | llm
result = chain.invoke({"input": "你好"})
```

#### Memory 模式 (对话)

```python
from langchain.memory import BufferWindowMemory

memory = BufferWindowMemory(k=5)
conversation = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=True
)
```

#### RAG 模式 (检索增强)

```python
# 1. 加载文档
loader = WebBaseLoader(urls)
docs = loader.load()

# 2. 切分文档
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
splits = text_splitter.split_documents(docs)

# 3. 创建向量索引
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings()
)

# 4. 创建检索链
retriever = vectorstore.as_retriever()
qa_chain = create_retrieval_chain(retriever, prompt | llm)
```

#### Agent 模式 (工具调用)

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor

# 定义工具
tools = [
    Tool(name="get_weather", func=get_weather, description="查询天气")
]

# 创建 agent
agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)
```

### 5. 部署架构模式

#### Python FastAPI 部署

```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    # 处理聊天请求
    pass

@app.on_event("startup")
async def startup_event():
    # 初始化资源
    pass
```

#### TypeScript Express 部署

```typescript
import express from 'express';
import cors from 'cors';

const app = express();

app.use(cors());
app.use(express.json());

app.post('/chat', async (req, res) => {
    // 处理聊天请求
});

app.listen(4001, () => {
    console.log('Server running on port 4001');
});
```

## 数据流模式

### 基础链式调用

```
用户输入 → Prompt Template → LLM → 输出
```

### RAG 流程

```
文档集合 → 切分 → 嵌入向量 → 向量数据库
                                    ↓
用户查询 → 检索相关文档 → Prompt → LLM → 回答
```

### Agent 流程

```
用户查询 → Agent 思考 → 选择工具 → 工具执行 → 观察结果 → 思考 → 最终回答
```

### 多智能体协作

```
用户查询 → Supervisor 分配任务 → Sub-agent 1 → 结果汇总
                ↓                   ↓
          Sub-agent 2 → Sub-agent 3 → 最终输出
```

## 配置管理

### 环境变量层次

1. **`.env` 文件**：本地开发配置（不提交）
2. **`.env.example`**：配置模板（提交到仓库）
3. **系统环境变量**：生产环境配置

### 配置验证

```python
def validate_env():
    required_vars = ["OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise ValueError(f"缺少环境变量: {', '.join(missing)}")
```

## 构建和打包策略

### Python

- **包管理器**：uv（比 pip 更快）
- **锁文件**：`uv.lock`（跨平台依赖解析）
- **打包工具**：Hatchling
- **部署方式**：Docker 容器或直接运行

### TypeScript

- **包管理器**：pnpm（节省磁盘空间）
- **锁文件**：`pnpm-lock.yaml`
- **打包工具**：TypeScript 编译器 + tsx
- **部署方式**：Docker 容器或 Node.js 运行时

## 扩展性设计

### 添加新示例

1. 创建目录：`XX-example-name/`
2. 添加文件：`README.md`, `example.py`, `example.ipynb`
3. 更新主 README 的示例清单
4. 添加 TypeScript 对应实现

### 支持新框架

项目结构支持轻松添加新框架（如 ai-sdk、claude-agent-sdk）：

```
agents-handbook/
├── langchain-python/
├── langchain-typescript/
├── ai-sdk/           # 新框架
├── claude-agent-sdk/ # 新框架
```

## 性能考虑

### 向量数据库

- **Chroma**：适合开发和测试，易于使用
- **FAISS**：生产环境，高性能，需要持久化

### 流式输出

```python
# Python 流式调用
async for chunk in astream_chain({"input": query}):
    print("chunk.content, end="", flush=True)
```

```typescript
// TypeScript 流式调用
const stream = await chain.stream({ input: query });
for await (const chunk of stream) {
    process.stdout.write(chunk.content);
}
```

## 安全最佳实践

1. **API 密钥管理**：永远不要提交 `.env` 文件
2. **输入验证**：使用 Pydantic/Zod 验证用户输入
3. **错误处理**：不要暴露敏感信息到错误消息
4. **CORS 配置**：生产环境限制允许的来源
5. **速率限制**：API 服务考虑添加速率限制

## 监控和追踪

### LangSmith 集成

```python
from langchain.callbacks.tracers import LangChainTracer

tracer = LangChainTracer(project_name="my-project")
chain = prompt | llm
chain.invoke({"input": "test"}, config={"callbacks": [tracer]})
```

### 日志记录

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("处理用户请求")
logger.error(f"处理失败: {error}")
```

## 测试策略

### 单元测试

- 测试单个函数和组件
- Mock 外部依赖（LLM、API）
- 快速执行

### 集成测试

- 测试完整的链和流程
- 使用真实的向量数据库
- 测试 API 端点

### 端到端测试

- 测试完整的用户场景
- 使用真实的 LLM API（需要测试密钥）
- 验证输出质量

## 未来扩展方向

1. **更多框架**：添加 ai-sdk、claude-agent-sdk 示例
2. **更多数据源**：数据库、文件系统、实时数据
3. **更多部署选项**：Kubernetes、Serverless
4. **性能优化**：缓存、批处理、并发
5. **安全性增强**：认证、授权、加密

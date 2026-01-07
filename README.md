# 🦜🔗 LangChain-Examples（Python & TypeScript）

- - https://docs.langchain.com/oss/python/langchain/overview

「一份同时覆盖 Python 与 TypeScript 的 LangChain v1.x 示例集合，帮助你用最短时间上手大模型应用开发。」

---

## 📌 项目定位
- 100% 基于 **LangChain 1.x**（Python ≥3.11，JS/TS）
- 一份代码，两份体验：同场景分别给出 Python 与 TypeScript 实现
- 从「Hello Chain」→「可部署智能体」逐步递进，每个示例均可在笔记本或容器里一键跑通
- 统一环境、统一配置、统一提示词，方便横向对比两种语言差异

---

## 🧱 技术栈
| 类别 | Python 方案 | TypeScript 方案 |
|---|---|---|
| 环境管理 | Miniconda + conda-lock | nvm + corepack(pnpm) |
| 依赖文件 | requirements.txt / pyproject.toml | package.json |
| 交互开发 | Jupyter Lab | －（可直接用 VSCode 调试） |
| 主框架 | langchain    | langchain   |
| LLM 调用 | openai、langchain-openai | openai、langchain-openai |
| 向量库 | Chroma、FAISS | chromadb |
| 部署 | FastAPI + Uvicorn | Express + tsx |
| 代码风格 | black / ruff | prettier / eslint |


- Python 环境管理 [Miniconda](https://docs.conda.io/projects/miniconda/en/latest/)
- Python 交互式开发环境 [Jupyter Lab](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html)
- 大模型应用开发框架 [LangChain](https://docs.langchain.com/oss/python/langchain/overview)
- [OpenAI Python SDK](https://github.com/openai/openai-python?tab=readme-ov-file#installation)

---

## 🗂️ 目录结构

```bash
langchain-examples/
  ├─ python/                 # Python 示例
  │  ├─ 00-env-validate/     # 环境自检
  │  ├─ 01-hello-chain/      # 最简 LLMChain
  │  ├─ 02-prompt-template/  # 提示词模板化
  │  ├─ 03-memory-chat/      # 带记忆对话
  │  ├─ 04-rag-qa/           # 检索增强问答
  │  ├─ 05-agent-weather/    # 获取天气智能体
  │  ├─ 06-api-deployment/   # FastAPI 封装
  │  └─ requirements.txt
  ├─ typescript/             # TypeScript 示例
  │  ├─ src/01-hello-chain.ts
  │  ├─ src/05-agent-weather.ts
  │  └─ package.json
  ├─ docs/                   # 配图 & 运行截图
  └─ README.md
```

---

## 🚀 一键启动
### Python
```bash
# 1. 创建环境
conda env create -f python/env.yml
conda activate lc-py

# 2. 验证
python python/00-env-validate/validate.py

# 3. 运行任意示例
jupyter lab python/01-hello-chain/
```

### TypeScript
```bash
# 1. 安装 & 构建
cd typescript
pnpm i
pnpm build

# 2. 运行示例
pnpm run:ex 05-agent-weather
```

---

## 📑 示例清单
| 编号 | 示例 | 关键词 | Python | TS | 说明 |
|---|---|---|---|---|---|
| 01 | Hello Chain | LLMChain✓ | ✅ | ✅ | 最小可运行链 |
| 02 | Prompt Template | 模板渲染✓ | ✅ | ✅ | 动态 system / human 模板 |
| 03 | Memory Chat | BufferWindowMemory✓ | ✅ | ✅ | 多轮对话带记忆 |
| 04 | RAG QA | WebBaseLoader + Chroma + RetrievalQA✓ | ✅ | ✅ | 爬文档→切片→向量→问答 |
| 05 | 获取天气智能体 | OpenAI Functions + APIWrapper✓ | ✅ | ✅ | 实时查询天气并绘图 |
| 06 | API 部署 | FastAPI / Express✓ | ✅ | ✅ | 把 05 封装成 HTTP 服务 |

---

## 🔑 常见配置
所有示例优先读取 `.env`：

```yaml
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
# 可选代理或转发

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
- [ ] 07 结构化输出（Pydantic / Zod）
- [ ] 08 多智能体协作（Supervisor 模式）
- [ ] 09 流式输出 + 前端 ChatUI
- [ ] 10 生产级日志、追踪（LangSmith）

---

## 🤝 贡献指南
1. Fork → 新建 `feat/xxx` 分支
2. 确保 `make lint` & `make test` 通过
3. 提交 PR，并勾选「允许维护者编辑」

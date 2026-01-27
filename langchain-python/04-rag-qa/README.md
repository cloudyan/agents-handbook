# 04 - RAG QA (检索增强问答)

## 📚 示例说明

本示例实现了完整的 RAG（检索增强生成）问答系统，参考 TypeScript 版本实现。

## ✨ 主要特性

### 🌐 实时文档获取
- 从 LangChain 官方文档网站获取内容
- 使用 BeautifulSoup 解析 HTML
- 自动降级到备用文档

### 🤖 Ollama 嵌入
- 使用本地 Ollama 服务
- 模型：`nomic-embed-text`
- 无需调用外部 API

### 🗄️ Chroma 向量存储
- 连接到 Docker 运行的 Chroma 服务
- 集合名称：`rag-qa-demo`
- 自动创建向量索引

### 🔍 智能检索
- 基于语义相似度检索
- 返回最相关的 3 个文档片段
- LCEL 链式调用

## 🚀 快速开始

### 前置要求

1. **Ollama 服务**
   ```bash
   # 安装 Ollama
   curl -fsSL https://ollama.com/install.sh | sh

   # 下载嵌入模型
   ollama pull nomic-embed-text

   # 启动服务
   ollama serve
   ```

2. **Chroma 服务（Docker）**
   ```bash
   docker run -d \
     -p 8000:8000 \
     chromadb/chroma:latest
   ```

3. **环境变量配置**
   ```bash
   # .env 文件
   OPENAI_API_KEY=your_api_key
   OPENAI_BASE_URL=https://api.deepseek.com/v1
   MODEL_NAME=deepseek-chat
   ```

### 运行示例

```bash
cd langchain-python
uv run python 04-rag-qa/rag_qa.py
```

## 📊 运行示例

```
问题: 关于 LangChain 你知道什么？
--------------------------------------------------
回答: LangChain 是一个用于快速构建由大语言模型（LLMs）驱动的智能体（agents）和应用程序的框架...

问题: LangChain 提供哪些核心功能？
--------------------------------------------------
回答: 根据上下文，LangChain 提供的核心功能包括：预构建的代理架构、与多种大语言模型的集成...

问题: 什么是机器学习？
--------------------------------------------------
回答: 无法回答。
```

## 🔧 配置选项

### 代码配置

```python
# 文档分割参数
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块大小
    chunk_overlap=50,   # 重叠大小
)

# 检索参数
retriever = vector_store.as_retriever(search_kwargs={"k": 3})  # 返回 3 个结果

# 嵌入模型
embeddings = create_embedding_client(
    use_ollama=True,
    model_name="nomic-embed-text",  # 或 "mxbai-embed-large"
)
```

### 环境变量

```env
# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434

# OpenAI 配置（用于 LLM）
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat
```

## 📝 代码结构

```python
# 1. 获取文档
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
body_text = soup.body.get_text()

# 2. 分割文档
chunks = text_splitter.split_text(body_text)

# 3. 创建向量索引
vector_store = Chroma.from_texts(
    texts=chunks,
    embedding=embeddings,
    collection_name="rag-qa-demo",
)

# 4. 创建 RAG 链
rag_chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. 问答
result = rag_chain.invoke(question)
```

## 🎯 学习目标

通过本示例，你将学习：

1. **RAG 原理**
   - 检索：从向量库检索相关文档
   - 增强：将检索到的文档作为上下文
   - 生成：基于上下文生成答案

2. **文档处理**
   - 网页抓取和解析
   - 文本分割和预处理
   - 向量化存储

3. **向量检索**
   - 语义相似度检索
   - Chroma 向量数据库
   - Ollama 嵌入模型

4. **LCEL 链式调用**
   - 使用 `|` 操作符连接组件
   - 自动处理数据流
   - 易于调试和扩展

## 🔍 故障排查

### Ollama 连接失败

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 启动 Ollama
ollama serve
```

### Chroma 连接失败

```bash
# 检查 Chroma 是否运行
curl http://localhost:8000/api/v1/heartbeat

# 启动 Chroma
docker run -d -p 8000:8000 chromadb/chroma:latest
```

### 文档获取失败

- 检查网络连接
- 检查防火墙设置
- 代码会自动使用备用文档

## 📚 相关文件

- `rag_qa.py` - 主程序
- `IMPLEMENTATION.md` - 详细实现说明
- `rag_qa.ipynb` - Jupyter Notebook（文档说明）

## 🆚 与 TypeScript 版本对比

| 特性 | Python | TypeScript |
|------|--------|------------|
| HTTP 客户端 | requests | axios |
| HTML 解析 | BeautifulSoup | cheerio |
| 嵌入模型 | Ollama | Ollama |
| 向量存储 | Chroma | Chroma |
| 链式调用 | LCEL | LCEL |

## 🎓 扩展练习

1. **添加更多文档源**
   - 支持本地文件
   - 支持多种格式（PDF、Markdown）
   - 添加文档更新机制

2. **改进检索质量**
   - 尝试不同的分割参数
   - 使用更高级的嵌入模型
   - 添加重排序（Reranking）

3. **添加缓存**
   - 缓存向量索引
   - 缓存嵌入结果
   - 提升响应速度

4. **支持多语言**
   - 使用多语言嵌入模型
   - 添加翻译功能
   - 支持跨语言检索

## 📖 参考资料

- [LangChain RAG 文档](https://python.langchain.com/docs/tutorials/rag/)
- [Ollama 官方文档](https://ollama.com/)
- [Chroma 官方文档](https://docs.trychroma.com/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/)

---

**状态**: ✅ 完全可用
**依赖**: Ollama, Chroma (Docker)
**参考**: TypeScript 版本 `src/04-rag-qa.ts`

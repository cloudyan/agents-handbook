# 04 - RAG QA 实现说明

## 🎯 实现特点

本实现参考 TypeScript 版本，完整实现了 RAG（检索增强生成）问答系统：

### ✅ 主要功能

1. **实时文档获取**
   - 从 `https://docs.langchain.com/oss/python/langchain/overview` 获取文档
   - 使用 BeautifulSoup 解析 HTML
   - 自动降级到备用文档（网络失败时）

2. **Ollama 嵌入**
   - 使用 `nomic-embed-text` 模型
   - 连接到本地 Ollama 服务 (`http://localhost:11434`)
   - 支持自定义模型和地址

3. **Chroma 向量存储**
   - 连接到 Docker 运行的 Chroma 服务
   - 集合名称：`rag-qa-demo`
   - 自动创建向量索引

4. **智能检索**
   - 使用 RecursiveCharacterTextSplitter 分割文档
   - 检索最相关的 3 个片段
   - LCEL 链式调用

## 🔧 配置要求

### 1. 环境变量

在 `.env` 文件中配置：

```env
# OpenAI API（用于 LLM）
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
MODEL_NAME=deepseek-chat

# Ollama 配置（可选）
OLLAMA_BASE_URL=http://localhost:11434
```

### 2. Ollama 服务

确保 Ollama 服务运行并安装嵌入模型：

```bash
# 安装 Ollama（如果还没有）
curl -fsSL https://ollama.com/install.sh | sh

# 下载嵌入模型
ollama pull nomic-embed-text

# 启动 Ollama 服务
ollama serve
```

### 3. Chroma 服务（Docker）

启动 Chroma Docker 容器：

```bash
docker run -d \
  -p 8000:8000 \
  -e CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER=chromadb.auth.token.TokenAuthServerProvider \
  -e CHROMA_SERVER_AUTH_CREDENTIALS=token12345 \
  chromadb/chroma:latest
```

或者使用 docker-compose：

```yaml
version: '3.8'
services:
  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    environment:
      - CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER=chromadb.auth.token.TokenAuthServerProvider
      - CHROMA_SERVER_AUTH_CREDENTIALS=token12345
```

## 🚀 运行步骤

### 1. 启动服务

```bash
# 启动 Ollama
ollama serve

# 启动 Chroma（Docker）
docker-compose up -d
```

### 2. 运行示例

```bash
cd langchain-python
uv run python 04-rag-qa/rag_qa.py
```

## 📊 运行流程

```
1. 获取文档
   ↓
2. 解析 HTML
   ↓
3. 分割文档（500 字符/块，重叠 50 字符）
   ↓
4. 使用 Ollama 嵌入
   ↓
5. 存储到 Chroma
   ↓
6. 创建 RAG 链
   ↓
7. 测试问答
```

## 🔍 测试结果

### 问题 1: 关于 LangChain 你知道什么？
✅ 成功回答，基于检索到的文档内容

### 问题 2: LangChain 提供哪些核心功能？
✅ 成功回答，提取了核心功能列表

### 问题 3: 什么是机器学习？
✅ 正确回答"无法回答"（文档中无相关信息）

## 📝 代码结构

```python
# 1. 导入库
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 2. 获取并解析文档
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')
body_text = soup.body.get_text()

# 3. 分割文档
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_text(body_text)

# 4. 创建向量索引
embeddings = create_embedding_client(use_ollama=True)
vector_store = Chroma.from_texts(texts=chunks, embedding=embeddings, ...)

# 5. 创建 RAG 链
rag_chain = (
    {"context": retriever | format_docs, "input": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 6. 测试问答
result = rag_chain.invoke(question)
```

## 🆚 与 TypeScript 版本对比

| 特性 | Python | TypeScript |
|------|--------|------------|
| 文档获取 | requests + BeautifulSoup | axios + cheerio |
| 嵌入模型 | Ollama (nomic-embed-text) | Ollama (nomic-embed-text) |
| 向量存储 | Chroma | Chroma |
| 链式调用 | LCEL | LCEL |
| 代码风格 | Pythonic | TypeScriptic |

## ⚠️ 注意事项

1. **网络访问**
   - 需要访问 `docs.langchain.com`
   - 如果失败会自动使用备用文档

2. **Ollama 模型**
   - 首次运行需要下载 `nomic-embed-text` 模型
   - 下载时间取决于网络速度

3. **Chroma 服务**
   - 确保 Chroma 服务运行在 `localhost:8000`
   - 首次运行会自动创建集合

4. **性能优化**
   - 文档分割大小可调整（`chunk_size`）
   - 检索数量可调整（`k` 参数）
   - 嵌入模型可更换（`mxbai-embed-large`）

## 🎓 学习要点

1. **RAG 原理**
   - 检索：从向量库检索相关文档
   - 增强：将检索到的文档作为上下文
   - 生成：基于上下文生成答案

2. **LCEL 链式调用**
   - 使用 `|` 操作符连接组件
   - 自动处理数据流
   - 易于调试和扩展

3. **向量嵌入**
   - 使用 Ollama 本地嵌入
   - 无需调用外部 API
   - 支持多种嵌入模型

## 🔧 故障排查

### 问题：无法连接 Ollama

```bash
# 检查 Ollama 是否运行
curl http://localhost:11434/api/tags

# 如果没有运行，启动 Ollama
ollama serve
```

### 问题：无法连接 Chroma

```bash
# 检查 Chroma 是否运行
curl http://localhost:8000/api/v1/heartbeat

# 如果没有运行，启动 Chroma
docker run -d -p 8000:8000 chromadb/chroma:latest
```

### 问题：文档获取失败

- 检查网络连接
- 检查防火墙设置
- 代码会自动使用备用文档

## 📚 扩展建议

1. **支持更多文档源**
   - 添加 PDF 文档支持
   - 添加 Markdown 文件支持
   - 添加 Word 文档支持

2. **改进检索质量**
   - 调整分割参数
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

---

**实现时间**: 2026-01-27
**状态**: ✅ 完全可用
**参考**: TypeScript 版本 `src/04-rag-qa.ts`

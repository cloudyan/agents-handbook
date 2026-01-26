# 搭建 RAG 的 embeddings 服务

1. Ollama（本地 LLM 服务）

```BASH
# macOS (使用 Homebrew)
brew install ollama
ollama serve

# 下载模型
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# 测试
ollama run qwen2.5:7b
```

2. ChromaDB（向量数据库）

```bash
# 使用 Docker（推荐）
docker run -d \
  --name chromadb \
  -p 8000:8000 \
  -v chroma-data:/chroma/chroma \
  chromadb/chroma:latest

# 或使用 Python
pip install chromadb
chromadb-server --host 0.0.0.0 --port 8000
```

3. FAISS（本地向量索引）

FAISS 不需要服务器，是纯本地库：

```bash
# Python
pip install faiss-cpu  # 或 faiss-gpu

# Node.js
npm install faiss-node
# 注意：需要编译，可能需要 Python 和 C++ 编译器
```

4. Redis（替代方案）

```bash
# 安装 Redis Stack（包含向量搜索）
docker run -d \
  --name redis-stack \
  -p 6379:6379 \
  redis/redis-stack-server:latest

# 或使用 Homebrew
brew install redis-stack
redis-stack-server
```
推荐方案

最简单：使用 ChromaDB Docker

    docker run -d --name chromadb -p 8000:8000 chromadb/chroma:latest

然后修改代码连接：

```ts
const vectorStore = await Chroma.fromTexts(
  chunks,
  {},
  embeddings,
  {
    collectionName: "rag-qa-demo",
    url: "http://localhost:8000",
  }
);
```

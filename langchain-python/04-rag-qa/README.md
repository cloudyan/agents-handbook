# 04 - RAG QA

学习检索增强生成（RAG）技术，通过文档检索来提高问答的准确性。

## 文件说明

- `rag_qa.ipynb` - Jupyter Notebook 版本，包含完整的 RAG 系统演示
- `rag_qa.py` - Python 脚本版本，核心 RAG 功能演示

## 运行方法

### Jupyter Notebook（推荐）

```bash
jupyter lab langchain-python/04-rag-qa/
```

然后打开 `rag_qa.ipynb` 按顺序执行单元格。

### Python 脚本

```bash
cd langchain-python
python 04-rag-qa/rag_qa.py
```

## 学习目标

- 理解 RAG 的基本原理和优势
- 掌握文档加载和预处理
- 学习向量化存储和检索
- 实现完整的 RAG 问答系统

## 主要内容

### 1. 文档准备和加载
- 创建示例文档
- 使用 TextLoader 加载本地文件
- 支持多种文档格式（txt, pdf, html 等）

### 2. 文档预处理
- RecursiveCharacterTextSplitter 文档分割
- 设置合适的 chunk_size 和 overlap
- 保持文档的语义完整性

### 3. 向量化存储
- OpenAIEmbeddings 文本向量化
- Chroma 向量数据库存储
- 持久化存储支持

### 4. 检索系统
- 相似性搜索
- 检索结果排序
- 动态添加新文档

### 5. RAG 问答链
- RetrievalQA 链的创建
- 自定义提示词模板
- 源文档引用

## 关键概念

### RAG 工作流程
```
文档 → 分割 → 向量化 → 存储 → 检索 → 生成回答
```

### 核心组件
- **Document Loader**: 文档加载器
- **Text Splitter**: 文档分割器
- **Embeddings**: 文本向量化
- **Vector Store**: 向量数据库
- **Retriever**: 检索器
- **RetrievalQA**: RAG 问答链

## 配置参数

### 文档分割参数
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 分块大小
    chunk_overlap=50,      # 重叠大小
    separators=["\n\n", "\n", " ", ""]  # 分割符优先级
)
```

### 检索参数
```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}  # 检索文档数量
)
```

### 提示词模板
```python
prompt_template = """
基于以下上下文信息回答问题。如果上下文中没有相关信息，请说明。

上下文：
{context}

问题：{question}

请提供准确、详细的回答：
"""
```

## 最佳实践

### 1. 文档分割
- **chunk_size**: 500-1000 字符通常效果较好
- **overlap**: 10-20% 的 chunk_size 作为重叠
- **separators**: 按语义重要性排序

### 2. 向量化
- 使用高质量的嵌入模型（如 OpenAI embeddings）
- 考虑嵌入成本和性能的平衡
- 批量处理提高效率

### 3. 检索策略
- **k 值选择**: 3-5 个文档通常足够
- **相似度阈值**: 过滤低相关性结果
- **混合检索**: 结合关键词和语义检索

### 4. 提示词设计
- 明确指示基于上下文回答
- 处理无相关信息的情况
- 控制回答的详细程度

## 应用场景

### 知识库问答
- 企业内部文档问答
- 技术文档查询
- 学术研究辅助

### 内容生成
- 基于资料的报告生成
- 个性化内容推荐
- 智能摘要生成

### 客服支持
- 产品文档问答
- 常见问题自动回答
- 技术支持辅助

## 性能优化

### 1. 存储优化
- 定期清理过期文档
- 使用压缩减少存储空间
- 考虑分布式存储

### 2. 检索优化
- 建立文档索引
- 缓存热门查询结果
- 使用近似最近邻算法

### 3. 生成优化
- 限制上下文长度
- 使用流式输出
- 批量处理查询

## 环境要求

- Python ≥ 3.11
- 已安装 requirements.txt 中的依赖
- 已设置 OPENAI_API_KEY 环境变量
- 足够的磁盘空间存储向量数据库

## 预期输出

```
🦜🔗 04 - RAG QA
========================================
✓ LangChain 组件导入完成

=== 1. 准备文档数据 ===
✓ 示例文档创建完成

=== 2. 加载和分割文档 ===
✓ 加载了 2 个文档
✓ 文档分割完成，共 4 个分块

=== 3. 创建向量数据库 ===
✓ 向量数据库创建完成

=== 4. 创建 RAG 问答链 ===
✓ RAG 问答链创建完成

=== 5. 测试 RAG 问答 ===

问题：Python 有哪些主要特点？
回答：根据提供的文档，Python 的主要特点包括...
[详细回答...]

问题：LangChain 提供哪些核心功能？
回答：根据提供的文档，LangChain 的核心功能包括...
[详细回答...]

=== 6. 添加新文档 ===
✓ 添加了 1 个新的文档分块

问题：什么是深度学习？
回答：根据提供的文档，深度学习是机器学习的一个子领域...
[详细回答...]

🎉 RAG QA 示例运行成功！
```

## 下一步

完成这个示例后，可以继续学习：
- 05 - Agent Weather（获取天气智能体）
- 06 - API Deployment（FastAPI 部署）

## 扩展学习

- 尝试不同的向量数据库（FAISS、Pinecone 等）
- 实现多文档源的 RAG 系统
- 添加文档相关性评分
- 实现增量更新和删除功能

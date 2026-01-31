# 01 - Hello Chain

最简单的 LangChain 示例，演示如何创建一个基本的 LLMChain。

## 文件说明

- `hello_chain.ipynb` - Jupyter Notebook 版本，适合学习和实验
- `hello_chain.py` - Python 脚本版本，适合直接运行

## 运行方法

### Jupyter Notebook（推荐）

#### 1. 安装 Jupyter Lab

```bash
# 使用 pip 安装
pip install jupyterlab

# 或使用 uv（项目推荐）
cd langchain-python
uv pip install jupyterlab
```

#### 2. 启动 Jupyter Lab

```bash
# 进入项目根目录
cd langchain-python

# 启动 Jupyter Lab
jupyter lab
# 或
./start_jupyter.sh
```

启动后会自动打开浏览器，或手动访问：`http://localhost:8888`

#### 3. 在 Jupyter Lab 中导航

```
agent-recipes/
└── langchain-python/
    ├── 01-hello-chain/
    │   └── hello_chain.ipynb  ← 点击这个文件
    └── ...
```

#### 4. 运行 Notebook

**逐个单元格运行**：
- 点击单元格，按 `Shift + Enter` 运行当前单元格并跳到下一个
- 或点击工具栏的 `▶ Run` 按钮

**全部运行**：
- 点击菜单：`Cell` → `Run All`
- 或点击工具栏的 `▶▶` 按钮

#### 5. 常用快捷键

| 快捷键 | 功能 |
|--------|------|
| `Shift + Enter` | 运行当前单元格，跳到下一个 |
| `Ctrl + Enter` | 运行当前单元格，不跳转 |
| `Alt + Enter` | 运行当前单元格，在下方插入新单元格 |
| `A` | 在上方插入单元格（编辑模式） |
| `B` | 在下方插入单元格（编辑模式） |
| `DD` | 删除当前单元格（编辑模式） |
| `M` | 切换为 Markdown 单元格（编辑模式） |
| `Y` | 切换为代码单元格（编辑模式） |

#### 6. Jupyter vs Python 脚本

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **Jupyter Notebook** | 可视化、交互式、逐步调试 | 需要浏览器、不适合自动化 | 学习、实验、演示 |
| **Python 脚本** | 快速、可自动化、易于部署 | 调试不够直观 | 生产环境、批处理 |

**推荐**：学习阶段使用 Jupyter，开发阶段使用 Python 脚本。

### Python 脚本

```bash
cd langchain-python
python 01-hello-chain/hello_chain.py
```

## 学习目标

- 理解 LangChain 的基本概念
- 创建第一个 LLMChain
- 使用 OpenAI 模型进行文本生成

## 关键概念

1. **ChatOpenAI**: LangChain 对 OpenAI API 的封装
2. **ChatPromptTemplate**: 用于创建结构化的提示词
3. **LLMChain**: 将模型和提示词组合成可重用的链

## 环境要求

- Python ≥ 3.11
- 已安装 requirements.txt 中的依赖
- 已设置 OPENAI_API_KEY 环境变量

## 预期输出

```
🦜🔗 01 - Hello Chain
========================================
✓ LangChain 组件导入完成
✓ OpenAI 模型初始化完成
✓ 提示词模板创建完成
✓ LLMChain 创建完成

问题：什么是 LangChain？请简单介绍一下。
回答：[AI 生成的回答...]

🎉 Hello Chain 运行成功！
```

### 语法

旧版 LLMChain:
- from langchain.chains import LLMChain
- chain = LLMChain(llm=llm, prompt=prompt_template)
- response = chain.run(question)

新版 LCEL:
- 使用管道操作符 |
- chain = prompt_template | llm | StrOutputParser()
- response = chain.invoke({"question": question})

**LCEL 是 LangChain 的链式表达式语言**

LCEL 优势:
1. 更简洁直观的语法
2. 自动支持流式输出
3. 自动支持批处理
4. 自动支持异步
5. 更好的类型安全

```python
# ====== 旧用法 (已弃用) ======
# from langchain.chains import LLMChain
# old_chain = LLMChain(
#     llm=llm,
#     prompt=prompt_template,
# )
# print("✓ 旧版 LLMChain 创建完成")
# old_response = old_chain.run(question)
# print(f"\n旧版回答：{old_response}")

# ====== 新用法 LCEL (推荐) ======
print("=" * 50)

chain = prompt_template | llm | StrOutputParser()
print("✓ LCEL Chain 创建完成")

response = chain.invoke({"question": question})
print(f"\n新版回答：{response}")
```

## 下一步

完成这个示例后，可以继续学习：
- 02 - Prompt Template（提示词模板化）
- 03 - Memory Chat（带记忆对话）

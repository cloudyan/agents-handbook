# 02 - Prompt Template

深入学习 LangChain 的提示词模板功能，学习如何创建动态和结构化的提示词。

## 文件说明

- `prompt_template.ipynb` - Jupyter Notebook 版本，包含详细示例和练习
- `prompt_template.py` - Python 脚本版本，核心功能演示

## 运行方法

### Jupyter Notebook（推荐）

```bash
jupyter lab langchain-python/02-prompt-template/
```

然后打开 `prompt_template.ipynb` 按顺序执行单元格。

### Python 脚本

```bash
cd langchain-python
python 02-prompt-template/prompt_template.py
```

## 学习目标

- 掌握 ChatPromptTemplate 的使用
- 学习动态变量替换
- 理解 System 和 Human 消息的区别
- 创建复杂的提示词模板

## 主要内容

### 1. 基础提示词模板
- 使用 `from_template()` 创建简单模板
- 通过 `{variable}` 占位符实现动态内容

### 2. System + Human 消息模板
- SystemMessagePromptTemplate：设定 AI 角色和行为
- HumanMessagePromptTemplate：包含用户的具体请求

### 3. 多角色对比
- 同一问题，不同角色给出不同回答
- 演示模板的灵活性和实用性

### 4. 条件模板
- 根据参数动态创建不同的模板
- 适应不同复杂度的场景

### 5. 实际应用
- 代码生成模板
- 技术解释模板
- 创意写作模板

## 关键概念

- **ChatPromptTemplate**: LangChain 的核心模板类
- **SystemMessage**: 系统消息，设定 AI 的身份和行为准则
- **HumanMessage**: 人类消息，包含具体的用户输入
- **变量替换**: 使用 `{variable}` 语法实现动态内容

## 最佳实践

1. **明确角色**: 在 System 消息中清晰定义 AI 的角色
2. **分离关注点**: System 消息定义行为，Human 消息包含具体任务
3. **有意义的变量名**: 使用描述性的变量名提高可读性
4. **适度复杂**: 根据应用场景调整模板的复杂度

## 示例模板结构

```
System: 你是一个专业的{role}。请用{tone}的语调回答问题。
Human: {question}
```

## 环境要求

- Python ≥ 3.11
- 已安装 requirements.txt 中的依赖
- 已设置 OPENAI_API_KEY 环境变量

## 下一步

完成这个示例后，可以继续学习：
- 03 - Memory Chat（带记忆对话）
- 04 - RAG QA（检索增强问答）

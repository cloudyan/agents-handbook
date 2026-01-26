# 03 - Memory Chat

学习如何在 LangChain 中实现带记忆的对话系统，让 AI 能够记住之前的对话内容。

## 文件说明

- `memory_chat.ipynb` - Jupyter Notebook 版本，包含详细的记忆功能演示
- `memory_chat.py` - Python 脚本版本，核心记忆功能演示

## 运行方法

### Jupyter Notebook（推荐）

```bash
jupyter lab langchain-python/03-memory-chat/
```

然后打开 `memory_chat.ipynb` 按顺序执行单元格。

### Python 脚本

```bash
cd langchain-python
python 03-memory-chat/memory_chat.py
```

## 学习目标

- 理解对话记忆的重要性
- 掌握 BufferWindowMemory 的使用
- 学习不同类型的记忆组件
- 实现连续的多轮对话

## 主要内容

### 1. BufferWindowMemory - 滑动窗口记忆
- 只保留最近的 k 轮对话
- 节省 token 使用量
- 适合长期对话场景

### 2. ConversationBufferMemory - 完整对话记忆
- 保留所有历史对话记录
- 保证对话的完整性
- 适合短期重要对话

### 3. 记忆组件的使用
- MessagesPlaceholder：为对话历史预留位置
- memory 参数：将记忆集成到 Chain 中
- return_messages：控制返回格式

### 4. 记忆管理
- 查看当前记忆内容
- 保存和加载记忆
- 清空记忆

### 5. 实际应用场景
- 客服对话系统
- 个人助理
- 教学辅导

## 关键概念

- **BufferWindowMemory**: 滑动窗口记忆，k 参数控制窗口大小
- **ConversationBufferMemory**: 完整对话记忆，保存所有历史
- **MessagesPlaceholder**: 提示词中的占位符，用于插入对话历史
- **记忆键**: memory_key 指定在提示词中的变量名

## 使用示例

```python
# 创建记忆组件
memory = BufferWindowMemory(k=5, return_messages=True)

# 创建带记忆的提示词
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个友好的 AI 助手"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

# 创建带记忆的 Chain
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory
)
```

## 记忆类型对比

| 类型 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| BufferWindowMemory | 节省 token，性能好 | 可能丢失重要信息 | 长期对话，聊天机器人 |
| ConversationBufferMemory | 完整保留历史 | token 消耗大 | 短期重要对话，客服 |

## 选择建议

### 窗口大小设置
- **聊天机器人**: k=5-10
- **客服系统**: k=10-20
- **个人助理**: k=3-7
- **教学辅导**: k=8-15

### 使用场景
1. **短期对话** → BufferWindowMemory
2. **长期对话** → BufferWindowMemory + 较大 k 值
3. **重要对话** → ConversationBufferMemory
4. **混合需求** → 自定义记忆策略

## 环境要求

- Python ≥ 3.11
- 已安装 requirements.txt 中的依赖
- 已设置 OPENAI_API_KEY 环境变量

## 预期输出

```
🦜🔗 03 - Memory Chat
========================================
✓ LangChain 组件导入完成
✓ 模型初始化完成
✓ BufferWindowMemory 创建完成
✓ 带记忆的提示词模板创建完成
✓ 带记忆的对话 Chain 创建完成

=== 开始对话测试 ===
用户：你好！我叫小明，今年 25 岁。
AI：你好小明！很高兴认识你...
用户：你还记得我的名字吗？
AI：当然记得！你叫小明...
用户：我多大了？
AI：你今年 25 岁...

=== 当前记忆内容 ===
1. 用户：你好！我叫小明，今年 25 岁。
2. AI：你好小明！很高兴认识你...
3. 用户：你还记得我的名字吗？
4. AI：当然记得！你叫小明...
5. 用户：我多大了？
6. AI：你今年 25 岁...

总共记忆了 6 条消息

🎉 Memory Chat 示例运行成功！
```

## 下一步

完成这个示例后，可以继续学习：
- 04 - RAG QA（检索增强问答）
- 05 - Agent Weather（获取天气智能体）

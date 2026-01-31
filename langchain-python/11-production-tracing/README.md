# 11 - 生产级追踪

展示如何使用 LangSmith 进行生产级追踪、日志记录和性能监控。

## ✨ 现代化升级

本示例已升级为使用 LangChain 1.0 最新 API：

### 主要改进
- ✅ 使用 `create_agent()` 替代旧的 `create_tool_calling_agent()`
- ✅ 引入 `with_tracking()` 上下文管理器，自动处理追踪和错误
- ✅ 统一使用 `{messages: [...]}` 消息格式
- ✅ 代码量减少约 20%，更简洁易读

### 代码对比

**旧版 API（已废弃）**：
```python
from langchain.agents import create_tool_calling_agent, AgentExecutor

prompt = ChatPromptTemplate.from_messages([
    ("system", "..."),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])
agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
response = executor.invoke({"input": "...", "agent_scratchpad": ...})
```

**新版 API（当前使用）**：
```python
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="..."
)
response = agent.invoke({
    "messages": [HumanMessage(content="...")]
})
```

**追踪方式对比**：

**旧版（手动追踪）**：
```python
monitor.start_tracking()
try:
    response = chain.invoke(...)
    metrics = monitor.end_tracking("chain_name", True)
except Exception as e:
    metrics = monitor.end_tracking("chain_name", False, str(e))
    print(f"错误: {e}")
```

**新版（自动追踪）**：
```python
with with_tracking("chain_name", monitor, logger):
    response = chain.invoke(...)
```

## 核心功能

### 1. LangSmith 追踪
- 完整的执行链路追踪
- Token 使用统计
- 延迟监控
- 错误追踪

### 2. 日志记录
- 结构化日志
- 多级别日志（DEBUG, INFO, WARNING, ERROR）
- 日志轮转和归档

### 3. 性能监控
- 响应时间统计
- 成功率监控
- 成本计算

## 环境配置

```bash
# LangSmith 配置
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=agent-recipes

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
```

## 获取 LangSmith API Key

1. 访问 https://smith.langchain.com/
2. 注册/登录账户
3. 点击右上角头像 → Settings → API Keys
4. 点击 "Create API Key"
5. 复制生成的 API Key

### 免费额度
- 每月 5000 次追踪
- 30 天数据保留
- 基础分析功能

## 运行方法

```bash
cd langchain-python
python 11-production-tracing/tracing_example.py
```

## 核心代码

### 启用追踪
```python
import os
os.environ[\"LANGSMITH_TRACING\"] = \"true\"
os.environ[\"LANGSMITH_API_KEY\"] = \"your-key\"
os.environ[\"LANGSMITH_PROJECT\"] = \"my-project\"
```

### 添加标签和元数据
```python
chain.invoke(
    {\"question\": \"问题\"},
    config={
        \"tags\": [\"production\", \"qa\"],
        \"metadata\": {\"user_id\": \"123\", \"version\": \"1.0\"}
    }
)
```

### 使用 with_tracking 自动追踪
```python
from utils import with_tracking, PerformanceMonitor, CustomCallbackHandler

monitor = PerformanceMonitor()
logger = CustomCallbackHandler()

with with_tracking("chain_name", monitor, logger):
    response = chain.invoke(...)
```

### 自定义回调
```python
from utils import CustomCallbackHandler

logger = CustomCallbackHandler()
logger.log("INFO", "自定义日志信息")
```

## 监控指标

### 关键指标
- **延迟**: 平均响应时间
- **成功率**: 成功/总请求数
- **Token 使用**: 输入/输出 Token 数
- **成本**: API 调用成本

### 性能分析
```python
# 查看执行时间
execution_time = end_time - start_time

# 计算 Token 成本
input_cost = input_tokens * 0.0015 / 1000
output_cost = output_tokens * 0.002 / 1000
total_cost = input_cost + output_cost
```

## 最佳实践

### 1. 环境隔离
- 开发、测试、生产使用不同项目
- 使用环境变量管理配置

### 2. 错误处理
- 捕获并记录所有异常
- 设置重试机制
- 监控错误率

### 3. 成本控制
- 设置 Token 限制
- 监控每日用量
- 优化提示词长度

### 4. 性能优化
- 使用缓存减少重复调用
- 批量处理请求
- 选择合适的模型

## LangSmith 功能

### 1. 执行追踪
查看完整的执行链路，包括：
- 每个步骤的输入输出
- Token 使用情况
- 执行时间

### 2. 数据集管理
- 创建测试数据集
- 运行批量评估
- 对比不同版本

### 3. 性能分析
- 响应时间分布
- 成功率统计
- 错误类型分析

### 4. 成本追踪
- Token 使用统计
- 成本趋势分析
- 预算预警

## 下一步

完成生产级追踪学习后，可以继续探索：
- 高级 RAG 优化
- 多模态处理
- 自定义 Agent 框架
- 部署和运维

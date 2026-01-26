# 11 - 生产级追踪

展示如何使用 LangSmith 进行生产级追踪、日志记录和性能监控。

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
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=agents-handbook

# OpenAI 配置
OPENAI_API_KEY=your_openai_api_key
```

## 获取 LangSmith API Key

1. 访问 https://smith.langchain.com/
2. 注册/登录账户
3. 创建新项目
4. 获取 API Key

## 运行方法

```bash
cd langchain-python/11-production-tracing
python tracing_example.py
```

## 核心代码

### 启用追踪
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"
```

### 添加标签和元数据
```python
chain.invoke(
    {"input": "问题"},
    config={
        "tags": ["production", "qa"],
        "metadata": {"user_id": "123", "version": "1.0"}
    }
)
```

### 自定义回调
```python
from langchain.callbacks import BaseCallbackHandler

class CustomHandler(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"LLM 调用开始: {prompts}")
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

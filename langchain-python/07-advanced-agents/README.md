# 07 - Advanced Agents

高级Agent模式示例，展示ReAct、Self-Ask、Plan-and-Execute等不同的Agent开发模式。

## 文件说明

- `advanced_agents.py` - 高级Agent模式实现
- `agent_comparison.py` - Agent性能对比分析
- `custom_agent_framework.py` - 自定义Agent框架

## 运行方法

```bash
cd langchain-python/07-advanced-agents
python advanced_agents.py
```

## Agent开发流程详解

### 🎯 第一步：理解Agent类型

#### 1. ReAct Agent (Reasoning and Acting)
```
工作流程：
Thought → Action → Observation → Thought → Action → ... → Final Answer
```

**特点：**
- 显式的推理过程
- 逐步执行和观察
- 适合需要详细推理的任务

**使用场景：**
- 数学问题求解
- 逻辑推理
- 多步骤问题解决

#### 2. Self-Ask Agent
```
工作流程：
Question → Follow-up Question → Answer → Follow-up Question → ... → Final Answer
```

**特点：**
- 自问自答模式
- 分解复杂问题
- 适合多跳查询

**使用场景：**
- 复杂知识问答
- 多步骤信息检索
- 研究型任务

#### 3. Plan-and-Execute Agent
```
工作流程：
Goal → Planning → Execution → Review → Adjustment → ... → Goal Completion
```

**特点：**
- 先规划后执行
- 支持动态调整
- 适合复杂项目管理

**使用场景：**
- 项目管理
- 复杂工作流
- 自动化任务

### 🔧 第二步：创建工具集

#### 工具设计原则
```python
@tool
def custom_tool(param1: str, param2: int) -> str:
    """工具描述，帮助Agent理解功能。

    Args:
        param1: 参数说明
        param2: 参数说明

    Returns:
        返回值说明
    """
    # 实现
    return result
```

#### 常用工具类型
1. **信息检索工具**
   - 数据库搜索
   - 网络搜索
   - 文档查询

2. **计算工具**
   - 数学计算
   - 数据分析
   - 统计处理

3. **交互工具**
   - API调用
   - 文件操作
   - 系统命令

4. **验证工具**
   - 数据验证
   - 结果检查
   - 错误处理

### 🏗️ 第三步：构建Agent

#### ReAct Agent构建
```python
# 1. 创建提示词模板
react_prompt = PromptTemplate.from_template("""
回答以下问题，你可以使用这些工具：

{tools}

使用以下格式：
Question: 问题
Thought: 思考过程
Action: 采取的行动
Action Input: 行动输入
Observation: 观察结果
... (重复)
Thought: 知道答案了
Final Answer: 最终答案

Question: {input}
Thought: {agent_scratchpad}
""")

# 2. 创建Agent
agent = create_react_agent(llm, tools, react_prompt)

# 3. 创建执行器
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
```

#### Self-Ask Agent构建
```python
# 1. 创建搜索工具
@tool
def search(query: str) -> str:
    """搜索工具实现"""
    return search_results

# 2. 创建Agent
agent = create_self_ask_with_search_agent(llm, search_tool)

# 3. 创建执行器
executor = AgentExecutor(agent=agent, tools=[search_tool])
```

#### Plan-and-Execute Agent构建
```python
class PlanExecuteAgent:
    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    def plan(self, goal: str) -> List[str]:
        """制定执行计划"""
        # 实现规划逻辑
        return plan_steps

    def execute(self, plan: List[str]) -> str:
        """执行计划"""
        # 实现执行逻辑
        return result

    def run(self, goal: str) -> str:
        """运行完整流程"""
        plan = self.plan(goal)
        result = self.execute(plan)
        return result
```

### 📊 第四步：性能优化

#### 1. 提示词优化
```python
# 优化前
simple_prompt = "回答问题：{input}"

# 优化后
optimized_prompt = """
你是一个专业的AI助手。请仔细分析用户问题，使用可用工具找到准确答案。

分析步骤：
1. 理解问题意图
2. 选择合适的工具
3. 执行并验证结果
4. 提供清晰答案

问题：{input}
思考过程：{agent_scratchpad}
"""
```

#### 2. 工具优化
```python
# 添加缓存
from functools import lru_cache

@tool
@lru_cache(maxsize=100)
def cached_search(query: str) -> str:
    """带缓存的搜索工具"""
    return search_implementation(query)

# 批量处理
@tool
def batch_search(queries: List[str]) -> List[str]:
    """批量搜索工具"""
    return [search(q) for q in queries]
```

#### 3. 执行优化
```python
# 并行执行
from concurrent.futures import ThreadPoolExecutor

def parallel_execute(tools_calls):
    """并行执行多个工具调用"""
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(call) for call in tools_calls]
        return [future.result() for future in futures]
```

### 🔍 第五步：测试和调试

#### 1. 单元测试
```python
def test_react_agent():
    agent = create_react_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools)

    response = executor.invoke({"input": "测试问题"})
    assert "Final Answer:" in response['output']
```

#### 2. 集成测试
```python
def test_agent_workflow():
    questions = [
        "简单问题",
        "复杂问题",
        "边界情况"
    ]

    for question in questions:
        response = agent_executor.invoke({"input": question})
        print(f"Q: {question}")
        print(f"A: {response['output']}")
```

#### 3. 性能测试
```python
import time

def benchmark_agent(agent, questions):
    """Agent性能基准测试"""
    start_time = time.time()

    for question in questions:
        response = agent.invoke({"input": question})

    end_time = time.time()
    avg_time = (end_time - start_time) / len(questions)

    print(f"平均响应时间：{avg_time:.2f}秒")
```

### 🚀 第六步：部署上线

#### 1. API封装
```python
from fastapi import FastAPI

app = FastAPI()

@app.post("/agent/react")
async def react_agent_endpoint(request: AgentRequest):
    response = react_executor.invoke({"input": request.message})
    return {"response": response['output']}
```

#### 2. 监控和日志
```python
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitored_agent_executor(agent_executor, input_data):
    """带监控的Agent执行"""
    logger.info(f"Agent输入：{input_data}")

    start_time = time.time()
    response = agent_executor.invoke(input_data)
    end_time = time.time()

    logger.info(f"执行时间：{end_time - start_time:.2f}秒")
    logger.info(f"Agent输出：{response['output'][:100]}...")

    return response
```

#### 3. 容错处理
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def robust_agent_execution(agent_executor, input_data):
    """带重试的Agent执行"""
    try:
        return agent_executor.invoke(input_data)
    except Exception as e:
        logger.error(f"Agent执行失败：{e}")
        raise
```

## 最佳实践总结

### ✅ 推荐做法
1. **明确的工具描述**：帮助Agent理解工具功能
2. **合理的错误处理**：优雅处理异常情况
3. **性能监控**：跟踪执行时间和成功率
4. **模块化设计**：便于维护和扩展
5. **充分测试**：确保各种场景下的稳定性

### ❌ 避免问题
1. **过度复杂的提示词**：影响理解和性能
2. **缺乏错误处理**：导致系统崩溃
3. **无限循环**：设置合理的执行限制
4. **硬编码逻辑**：降低系统的灵活性
5. **忽略安全性**：工具调用需要安全验证

## 环境要求

- Python ≥ 3.11
- LangChain ≥ 0.1.0
- OpenAI API Key
- 足够的计算资源用于复杂Agent

## 下一步

完成高级Agent学习后，可以继续探索：
- 多Agent协作系统
- 自定义Agent框架
- Agent性能优化
- 生产级部署方案

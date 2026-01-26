# 09 - 多智能体协作

多智能体协作系统，展示如何通过 Supervisor 模式协调多个专业 Agent 完成复杂任务。

## 核心概念

### Supervisor 模式
```
用户请求 → Supervisor Agent → 分配任务 → 子 Agent 执行 → 汇总结果 → 返回答案
```

**特点：**
- 一个管理 Agent（Supervisor）协调多个专业 Agent
- 每个 Agent 专注于特定领域
- 动态任务分配和结果聚合
- 支持并行执行

### Agent 角色设计

1. **Researcher Agent** - 信息搜集和研究
2. **Coder Agent** - 代码编写和调试
3. **Reviewer Agent** - 代码审查和质量检查
4. **Planner Agent** - 任务规划和分解

## 运行方法

```bash
cd langchain-python/09-multi-agent
python multi_agent_system.py
```

## 环境要求

- Python ≥ 3.11
- LangChain ≥ 0.1.0
- OpenAI API Key
- Tavily API Key（用于搜索功能）

## 示例场景

### 场景 1：代码开发流程
```
用户：帮我实现一个快速排序算法
↓
Planner：分解任务 → 1. 研究排序算法 2. 编写代码 3. 审查代码
↓
Researcher：搜索快速排序最佳实践
↓
Coder：编写 Python 快速排序实现
↓
Reviewer：检查代码质量和性能
↓
Supervisor：汇总结果，提供完整方案
```

### 场景 2：技术调研
```
用户：比较 React 和 Vue 的优缺点
↓
Planner：制定调研计划
↓
Researcher：搜集 React 和 Vue 的资料
↓
Reviewer：分析和对比技术指标
↓
Supervisor：生成对比报告
```

## 关键技术点

### 1. Agent 通信
```python
class AgentMessage:
    sender: str
    receiver: str
    content: str
    context: Dict[str, Any]
```

### 2. 任务分配
```python
def assign_task(self, task: str) -> List[Agent]:
    """根据任务类型分配给合适的 Agent"""
    if "代码" in task:
        return [self.coder_agent]
    elif "研究" in task:
        return [self.researcher_agent]
    else:
        return [self.researcher_agent, self.coder_agent]
```

### 3. 结果聚合
```python
def aggregate_results(self, results: List[str]) -> str:
    """整合多个 Agent 的结果"""
    return self.supervisor_llm.invoke(f"整合以下结果：{results}")
```

## 最佳实践

1. **明确 Agent 职责**：每个 Agent 专注于单一功能
2. **清晰的通信协议**：定义消息格式和传递规则
3. **容错机制**：处理 Agent 执行失败的情况
4. **性能监控**：跟踪各 Agent 的执行时间和成功率
5. **动态调整**：根据任务复杂度调整 Agent 数量

## 扩展方向

- **LangGraph**：使用状态机管理复杂工作流
- **多轮对话**：支持 Agent 之间的多轮交互
- **优先级队列**：根据任务重要性安排执行顺序
- **负载均衡**：在多个相同类型的 Agent 间分配任务

## 下一步

完成多智能体学习后，可以继续探索：
- 10-流式输出 + ChatUI
- 11-生产级追踪（LangSmith）
- 自定义 Agent 框架开发

# 09 多智能体系统 - 流程详解与改进方案

## 📋 当前实现的问题

### 问题 1：任务类型识别不准确

**当前实现**：
```typescript
private analyzeTaskType(task: string): string {
  const codeKeywords = ["实现", "编写", "代码", "函数", "算法", "程序"];
  const researchKeywords = ["研究", "分析", "比较", "调研", "技术"];

  const taskLower = task.toLowerCase();

  if (codeKeywords.some((kw) => taskLower.includes(kw))) {
    return "code_development";
  } else if (researchKeywords.some((kw) => taskLower.includes(kw))) {
    return "research";
  } else {
    return "general";
  }
}
```

**问题**：
- ❌ 纯字符串匹配，容易误判
- ❌ 关键词列表有限，覆盖不全
- ❌ 无法理解语义和上下文
- ❌ "研究如何实现" 这种任务会误判为 "research"

**例子**：
```
"研究如何实现快速排序" → 会被识别为 "research"
"实现一个研究工具" → 会被识别为 "code_development"
"分析代码性能" → 会被识别为 "research"
```

---

### 问题 2：固定流程，缺乏灵活性

**当前实现**：
```typescript
private async coordinateCodeDevelopment(task: string): Promise<string> {
  // 固定执行三个步骤
  // 1. Researcher
  // 2. Coder
  // 3. Reviewer
}
```

**问题**：
- ❌ 无论任务简单复杂，都执行全部三个 Agent
- ❌ 无法跳过不需要的步骤
- ❌ 无法根据结果动态调整流程
- ❌ 无法处理异常情况（如研究失败）

**例子**：
```
任务："实现一个简单的加法函数"
→ 当前：Researcher → Coder → Reviewer（3个步骤）
→ 更好：Coder → Reviewer（跳过研究）

任务："研究 Python 特性"
→ 当前：只执行 Researcher
→ 更好：可以跳过代码和审查，但如果需要示例代码，应该动态决定
```

---

### 问题 3：数据流转写死，不够灵活

**当前实现**：
```typescript
// Supervisor → Researcher
const researchMessage = researcher.sendMessage("Supervisor", `研究如何${task}`);
const researchResponse = await researcher.receiveMessage(researchMessage);

// Researcher → Coder (固定拼接)
const codeTask = researchReport
  ? `根据以下研究报告编写代码：\n\n${researchReport}\n\n任务：${task}`
  : task;

// Coder → Reviewer (直接传递代码)
const reviewMessage = reviewer.sendMessage("Supervisor", codeContent);
```

**问题**：
- ❌ 数据格式固定（字符串拼接）
- ❌ 无法筛选和过滤信息
- ❌ 无法添加额外的上下文
- ❌ 无法处理结构化数据

---

## 🔄 当前数据流转图

```
用户请求
    ↓
Supervisor.analyzeTaskType() [字符串匹配]
    ↓
Supervisor.coordinateCodeDevelopment()
    ↓
    ├─→ Researcher
    │       ├─ 接收: "研究如何实现快速排序"
    │       ├─ 处理: 搜索 + LLM 生成报告
    │       └─ 返回: "研究报告：..." (researchReport)
    │
    └─→ Coder
            ├─ 接收: "根据以下研究报告编写代码：\n\n{researchReport}\n\n任务：实现快速排序"
            ├─ 处理: LLM 编写代码
            └─ 返回: "代码实现：..." (codeContent)

        └─→ Reviewer
                ├─ 接收: "代码实现：..." (codeContent)
                ├─ 处理: LLM 审查代码
                └─ 返回: "审查报告：..." (reviewReport)

Supervisor.summarizeResults()
    ↓
汇总所有结果
    ↓
返回最终结果
```

**关键点**：
1. **单向传递**：Supervisor → Researcher → Coder → Reviewer
2. **固定格式**：每个环节都把之前的全部内容拼接传给下一个
3. **无反馈循环**：Reviewer 发现问题无法反馈给 Coder 修正
4. **结构简单**：所有数据都是字符串，没有结构化

---

## 💡 改进方案

### 改进 1：使用 LLM 进行任务类型识别

```typescript
private async analyzeTaskTypeWithLLM(task: string): Promise<string> {
  const classificationPrompt = `分析以下任务类型，返回 JSON 格式：

任务：${task}

可用类型：
- code_development: 需要编写、实现或修改代码
- research: 纯粹的信息搜集和分析
- general: 其他通用任务

返回格式：
{
  "type": "code_development|research|general",
  "confidence": 0.0-1.0,
  "reasoning": "判断理由"
}`;

  const response = await this.llm.invoke(classificationPrompt);
  const result = JSON.parse(response.content as string);

  console.log(`[Supervisor] 任务分类: ${result.type} (置信度: ${result.confidence})`);
  console.log(`[Supervisor] 判断理由: ${result.reasoning}`);

  return result.type;
}
```

**优点**：
- ✅ 理解语义和上下文
- ✅ 提供置信度和理由
- ✅ 可以处理复杂任务描述
- ✅ 容易扩展新类型

---

### 改进 2：动态工作流，基于 LLM 决策

```typescript
private async coordinateCodeDevelopmentDynamic(task: string): Promise<string> {
  const results: string[] = [];

  // 步骤 1：使用 LLM 决定是否需要研究
  const needsResearch = await this.decideNeedsResearch(task);
  console.log(`[Supervisor] 需要研究: ${needsResearch}`);

  let researchReport = "";
  if (needsResearch) {
    const researcher = this.agents.get("Researcher")!;
    const researchMessage = researcher.sendMessage("Supervisor", `研究如何${task}`);
    const researchResponse = await researcher.receiveMessage(researchMessage);
    if (researchResponse) {
      researchReport = researchResponse.content;
      results.push(researchReport);
    }
  }

  // 步骤 2：使用 LLM 决定是否需要审查
  const codeTask = researchReport
    ? `根据以下研究报告编写代码：\n\n${researchReport}\n\n任务：${task}`
    : task;

  const coder = this.agents.get("Coder")!;
  const codeMessage = coder.sendMessage("Supervisor", codeTask);
  const codeResponse = await coder.receiveMessage(codeMessage);
  const codeContent = codeResponse?.content || "";

  results.push(codeContent);

  const needsReview = await this.decideNeedsReview(task, codeContent);
  console.log(`[Supervisor] 需要审查: ${needsReview}`);

  if (needsReview) {
    const reviewer = this.agents.get("Reviewer")!;
    const reviewMessage = reviewer.sendMessage("Supervisor", codeContent);
    const reviewResponse = await reviewer.receiveMessage(reviewMessage);
    if (reviewResponse) {
      results.push(reviewResponse.content);
    }
  }

  return await this.summarizeResults(task, results);
}

private async decideNeedsResearch(task: string): Promise<boolean> {
  const prompt = `判断以下任务是否需要先进行研究：

任务：${task}

考虑因素：
1. 是否涉及不熟悉的技术或算法
2. 是否需要查找最佳实践
3. 是否需要了解相关文档

返回 JSON：
{
  "needs_research": true/false,
  "reason": "理由"
}`;

  const response = await this.llm.invoke(prompt);
  const result = JSON.parse(response.content as string);
  return result.needs_research;
}

private async decideNeedsReview(task: string, code: string): Promise<boolean> {
  const prompt = `判断以下代码是否需要审查：

任务：${task}
代码长度：${code.length} 字符

考虑因素：
1. 代码复杂度
2. 任务重要性
3. 是否涉及关键功能

返回 JSON：
{
  "needs_review": true/false,
  "reason": "理由"
}`;

  const response = await this.llm.invoke(prompt);
  const result = JSON.parse(response.content as string);
  return result.needs_review;
}
```

**优点**：
- ✅ 根据任务复杂度动态调整流程
- ✅ 简单任务可以跳过不必要的步骤
- ✅ 复杂任务可以增加更多步骤
- ✅ 节省时间和成本

---

### 改进 3：结构化数据流转

```typescript
// 定义结构化消息类型
interface StructuredMessage {
  type: "task" | "research_result" | "code" | "review" | "error";
  content: string;
  metadata?: {
    task: string;
    timestamp: string;
    agent: string;
    confidence?: number;
  };
  data?: any; // 结构化数据
}

class ImprovedSupervisorAgent {
  private messageQueue: StructuredMessage[] = [];

  async coordinateTaskWithStructuredData(userRequest: string): Promise<string> {
    const results: StructuredMessage[] = [];

    // 步骤 1：研究
    const researchResult = await this.executeResearch(userRequest);
    if (researchResult) {
      results.push(researchResult);
    }

    // 步骤 2：编码（传入结构化数据）
    const codeResult = await this.executeCoding(userRequest, researchResult);
    if (codeResult) {
      results.push(codeResult);
    }

    // 步骤 3：审查（传入结构化数据）
    const reviewResult = await this.executeReview(codeResult);
    if (reviewResult) {
      results.push(reviewResult);
    }

    return this.summarizeStructuredResults(userRequest, results);
  }

  private async executeResearch(
    task: string
  ): Promise<StructuredMessage | null> {
    const researcher = this.agents.get("Researcher")!;
    const message: StructuredMessage = {
      type: "task",
      content: `研究如何${task}`,
      metadata: {
        task,
        timestamp: new Date().toISOString(),
        agent: "Supervisor",
      },
    };

    const response = await researcher.processStructuredMessage(message);

    return response;
  }

  private async executeCoding(
    task: string,
    researchResult?: StructuredMessage | null
  ): Promise<StructuredMessage | null> {
    const coder = this.agents.get("Coder")!;

    // 构建结构化输入
    const message: StructuredMessage = {
      type: "task",
      content: `实现：${task}`,
      metadata: {
        task,
        timestamp: new Date().toISOString(),
        agent: "Supervisor",
      },
      data: {
        research_summary: researchResult?.content,
        task_complexity: researchResult?.data?.complexity,
      },
    };

    const response = await coder.processStructuredMessage(message);
    return response;
  }

  private async executeReview(
    codeResult?: StructuredMessage | null
  ): Promise<StructuredMessage | null> {
    if (!codeResult) return null;

    const reviewer = this.agents.get("Reviewer")!;

    const message: StructuredMessage = {
      type: "task",
      content: "审查代码",
      metadata: {
        task: codeResult.metadata?.task || "unknown",
        timestamp: new Date().toISOString(),
        agent: "Supervisor",
      },
      data: {
        code: codeResult.content,
        code_length: codeResult.content.length,
        language: codeResult.data?.language,
      },
    };

    const response = await reviewer.processStructuredMessage(message);
    return response;
  }

  private async summarizeStructuredResults(
    task: string,
    results: StructuredMessage[]
  ): Promise<string> {
    const summaryPrompt = `汇总以下任务执行结果：

任务：${task}

执行过程：
${results
  .map(
    (r, i) =>
      `${i + 1}. ${r.type} 由 ${r.metadata?.agent} 执行\n   内容: ${r.content.slice(0, 200)}...`
  )
  .join("\n\n")}

请提供：
1. 任务完成情况
2. 关键成果
3. 建议
4. 下一步行动`;

    const response = await this.llm.invoke(summaryPrompt);
    return response.content as string;
  }
}
```

**优点**：
- ✅ 数据结构化，易于解析和处理
- ✅ 可以携带元数据（时间戳、置信度等）
- ✅ 支持复杂的数据类型
- ✅ 便于调试和追踪

---

### 改进 4：支持反馈循环

```typescript
class SupervisorWithFeedback {
  async coordinateTaskWithFeedback(task: string): Promise<string> {
    let iteration = 0;
    const maxIterations = 3;

    while (iteration < maxIterations) {
      iteration++;
      console.log(`\n[Supervisor] 第 ${iteration} 轮迭代`);

      // 执行研究
      const researchResult = await this.executeResearch(task);

      // 执行编码
      const codeResult = await this.executeCoding(task, researchResult);

      // 执行审查
      const reviewResult = await this.executeReview(codeResult);

      // 检查是否需要修改
      const needsRevision = await this.checkNeedsRevision(reviewResult);

      if (!needsRevision) {
        console.log(`[Supervisor] 审查通过，任务完成`);
        return await this.summarizeResults(task, [
          researchResult,
          codeResult,
          reviewResult,
        ]);
      }

      console.log(`[Supervisor] 需要修改，进入下一轮迭代`);

      // 将审查意见反馈给编码器
      const revisedCode = await this.reviseCode(
        codeResult.content,
        reviewResult.content,
        task
      );

      // 更新代码结果
      codeResult.content = revisedCode;
    }

    console.log(`[Supervisor] 达到最大迭代次数，返回当前结果`);
    return await this.summarizeResults(task, [codeResult]);
  }

  private async checkNeedsRevision(reviewResult: string): Promise<boolean> {
    const prompt = `分析以下审查报告，判断是否需要修改代码：

审查报告：
${reviewResult}

返回 JSON：
{
  "needs_revision": true/false,
  "critical_issues": ["问题1", "问题2"],
  "reason": "理由"
}`;

    const response = await this.llm.invoke(prompt);
    const result = JSON.parse(response.content as string);
    return result.needs_revision;
  }

  private async reviseCode(
    originalCode: string,
    reviewFeedback: string,
    task: string
  ): Promise<string> {
    const coder = this.agents.get("Coder")!;
    const message = {
      sender: "Supervisor",
      receiver: "Coder",
      content: `根据以下审查意见修改代码：

原代码：
${originalCode}

审查意见：
${reviewFeedback}

任务：${task}`,
    };

    const response = await coder.processMessage(message);
    return response?.content || originalCode;
  }
}
```

**优点**：
- ✅ 支持多轮迭代优化
- ✅ 审查发现问题可以反馈修改
- ✅ 提高代码质量
- ✅ 可控的迭代次数

---

## 🎯 完整改进方案对比

| 维度 | 当前实现 | 改进方案 |
|------|---------|---------|
| **任务识别** | 字符串匹配 | LLM 分类 + 置信度 |
| **流程控制** | 固定三步 | 动态决策 + 条件分支 |
| **数据格式** | 字符串拼接 | 结构化消息 |
| **反馈机制** | 无反馈 | 多轮迭代 + 反馈循环 |
| **灵活性** | 低 | 高 |
| **复杂度** | 简单 | 中等 |
| **成本** | 低 | 中等（额外 LLM 调用） |

---

## 📊 数据流转对比

### 当前流向
```
Supervisor → Researcher → Coder → Reviewer
    ↓           ↓            ↓           ↓
  字符串      字符串       字符串      字符串
```

### 改进流向
```
Supervisor → Researcher → Coder → Reviewer
    ↓           ↓            ↓           ↓
Structured  Structured   Structured  Structured
Message     Message      Message     Message
    ↓                              ↓
    └──────── 反馈循环 ─────────────┘
```

---

## 🚀 实施建议

### 阶段 1：快速改进（1-2 天）
1. 使用 LLM 替代字符串匹配进行任务分类
2. 添加决策逻辑判断是否需要研究步骤

### 阶段 2：结构化数据（3-5 天）
1. 定义 StructuredMessage 接口
2. 修改所有 Agent 支持结构化消息
3. 添加元数据追踪

### 阶段 3：反馈机制（5-7 天）
1. 实现审查结果分析
2. 添加代码修订功能
3. 支持多轮迭代

### 阶段 4：优化和测试（持续）
1. 性能优化
2. 添加缓存
3. 完善测试

---

## 💡 总结

当前实现适合：
- ✅ 学习多智能体概念
- ✅ 简单任务演示
- ✅ 快速原型开发

改进方案适合：
- ✅ 生产环境部署
- ✅ 复杂任务处理
- ✅ 高质量要求

**建议**：根据实际需求选择合适的方案，不必一次性实现所有改进。可以逐步迭代，从最关键的问题开始优化。

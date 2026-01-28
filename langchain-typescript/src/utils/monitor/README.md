# 监控工具使用指南

## 快速开始

### 方式 1：简单模式

```typescript
import { createTracer } from "./utils/monitor";

const tracer = createTracer();

// 手动追踪
tracer.monitor.startTracking();
try {
  const response = await chain.invoke({ question: "你好" });
  console.log(response);
  tracer.monitor.endTracking("simple_chain", true);
} catch (e) {
  tracer.monitor.endTracking("simple_chain", false, e.message);
  tracer.logger.error(e.message);
}

// 保存结果
await tracer.monitor.saveMetrics();
await tracer.logger.saveLogs();
```

### 方式 2：自动模式（推荐）

```typescript
import { createTracer, withTracking } from "./utils/monitor";

const tracer = createTracer({
  autoSave: true,  // 自动保存
  metricsFile: "metrics.json",
  logsFile: "logs.txt"
});

// 自动追踪
await withTracking("chain_name", tracer.monitor, tracer.logger, async () => {
  const response = await chain.invoke({ question: "你好" });
  console.log(response);
  return response;
});
```

## 在其他示例中使用

### 示例 05：天气智能体

```typescript
// 05-agent-weather/agent_weather.ts
import { createTracer, withTracking } from "../utils/monitor";

async function main() {
  const tracer = createTracer();

  await withTracking("weather_agent", tracer.monitor, tracer.logger, async () => {
    const response = await agent.invoke({
      messages: [new HumanMessage("明天需要带伞吗？")]
    });
    console.log(response);
  });

  await tracer.monitor.saveMetrics();
}
```

### 示例 07：高级 Agent

```typescript
// 07-advanced-agents/advanced_agents.ts
import { createTracer, withTracking } from "../utils/monitor";

const tracer = createTracer();

// ReAct Agent
await withTracking("react_agent", tracer.monitor, tracer.logger, async () => {
  const result = await reactAgent.invoke({ input: "什么是量子计算？" });
  console.log(result);
});

// Self-Ask Agent
await withTracking("self_ask_agent", tracer.monitor, tracer.logger, async () => {
  const result = await selfAskAgent.invoke({ input: "中国的首都是哪里？" });
  console.log(result);
});

await tracer.monitor.saveMetrics();
```

### 示例 10：流式聊天

```typescript
// 10-streaming-chat/index.ts
import { ProductionMonitor } from "../utils/monitor";

const monitor = new ProductionMonitor();

wss.on("connection", (ws) => {
  ws.on("message", async (data) => {
    monitor.startTracking();
    try {
      for await (const chunk of streamResponse(llm, message, session)) {
        ws.send(chunk);
      }
      monitor.endTracking("chat_stream", true);
    } catch (e) {
      monitor.endTracking("chat_stream", false, e.message);
    }
  });
});

// 定期保存指标
setInterval(() => {
  monitor.saveMetrics();
}, 60000); // 每分钟保存一次
```

## 配置选项

```typescript
const tracer = createTracer({
  autoSave: false,              // 是否自动保存
  metricsFile: "metrics.json",  // 指标文件名
  logsFile: "logs.txt"          // 日志文件名
});
```

## LangSmith 追踪配置

### 获取 LANGSMITH_API_KEY

LangSmith 是 LangChain 官方的追踪和调试平台，提供详细的执行追踪、性能分析和调试功能。

#### 步骤 1：注册 LangSmith 账号

访问 [https://smith.langchain.com/](https://smith.langchain.com/) 并注册账号。

#### 步骤 2：创建 API Key

1. 登录后，点击右上角头像
2. 选择 **Settings** → **API Keys**
3. 点击 **Create API Key** 按钮
4. 复制生成的 API Key

#### 步骤 3：配置环境变量

在项目根目录的 `.env` 文件中添加：

```bash
# LangSmith 追踪配置
LANGSMITH_API_KEY=lsk_your_api_key_here
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=your-project-name
```

#### 步骤 4：验证配置

运行示例后，如果看到以下输出，说明配置成功：

```
✓ LangSmith 追踪已启用
```

访问 [https://smith.langchain.com/](https://smith.langchain.com/) 可以查看详细的执行追踪。

### LangSmith 功能特性

- **执行追踪**：查看每一步的输入输出
- **性能分析**：识别性能瓶颈
- **成本监控**：追踪 token 使用和成本
- **调试工具**：快速定位问题
- **团队协作**：与团队成员共享追踪结果

### 免费额度

LangSmith 提供免费额度，包括：
- 每月 5000 次追踪
- 30 天数据保留
- 基础分析功能

超出免费额度后，需要升级付费计划。

### 不使用 LangSmith

如果不想使用 LangSmith，可以不配置 `LANGSMITH_API_KEY`，监控工具仍然会正常工作，只是不会上传到 LangSmith 平台。

```bash
# 不配置 LANGSMITH_API_KEY
# LANGSMITH_API_KEY=
# LANGSMITH_TRACING=false
```

运行时会看到：

```
⚠️  未设置 LANGSMITH_API_KEY，LangSmith 追踪已禁用
   访问 https://smith.langchain.com/ 获取 API Key
```

## API 参考

### ProductionMonitor

```typescript
const monitor = new ProductionMonitor(config);

monitor.startTracking();                    // 开始追踪
const metrics = monitor.endTracking("chain_name", true);  // 结束追踪
monitor.getSummary();                       // 获取摘要
await monitor.saveMetrics();                // 保存指标
monitor.getMetrics();                       // 获取所有指标
monitor.clearMetrics();                     // 清空指标
```

### CustomLogger

```typescript
const logger = new CustomLogger("logs.txt");

logger.info("信息");     // INFO 级别
logger.warn("警告");     // WARN 级别
logger.error("错误");    // ERROR 级别
logger.debug("调试");    // DEBUG 级别
await logger.saveLogs(); // 保存日志
logger.getLogs();        // 获取所有日志
logger.clearLogs();      // 清空日志
```

### withTracking

```typescript
const result = await withTracking(
  "chain_name",           // 链名称
  monitor,                // 监控器
  logger,                 // 日志器
  async () => {           // 要追踪的函数
    return await chain.invoke({ input: "test" });
  }
);
```

## 输出示例

### metrics.json

```json
{
  "timestamp": "2024-01-27T10:00:00.000Z",
  "summary": {
    "totalRuns": 4,
    "successfulRuns": 4,
    "failedRuns": 0,
    "successRate": 1.0,
    "averageTime": 2.5,
    "totalTokens": 1200,
    "estimatedCost": 0.024
  },
  "metrics": [
    {
      "chainName": "simple_chain",
      "executionTime": 1.2,
      "inputTokens": 10,
      "outputTokens": 50,
      "totalTokens": 60,
      "success": true,
      "errorMessage": ""
    }
  ]
}
```

### logs.txt

```
[2024/1/27 10:00:00] [INFO] 开始执行 simple_chain
[2024/1/27 10:00:01] [INFO] simple_chain 执行成功
[2024/1/27 10:00:02] [ERROR] agent_chain 错误: API 超时
```

## 最佳实践

1. **使用 `withTracking`**：自动处理错误追踪，代码更简洁
2. **设置有意义的链名称**：便于识别和统计
3. **定期保存指标**：长时间运行的应用建议定时保存
4. **结合 LangSmith**：配置 `LANGSMITH_API_KEY` 获取更详细的追踪信息
5. **监控成本**：通过 `estimatedCost` 估算 API 调用成本

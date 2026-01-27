# 12 - 完整聊天服务

一个生产级的 LangChain Agent 聊天服务，支持工具调用、流式输出、会话管理和数据分析。

## 核心功能

- ✅ **智能 Agent**：集成天气查询、数学计算、网络搜索工具
- ✅ **流式输出**：SSE 实时流式响应
- ✅ **会话管理**：支持多会话、历史记录、状态跟踪
- ✅ **数据分析**：会话统计、使用分析、性能监控
- ✅ **标准化 API**：RESTful 接口设计，易于对接

## 技术栈

- **框架**：Express + LangChain 1.0
- **模型**：OpenAI 兼容接口（DeepSeek/GPT-4o）
- **工具**：OpenWeather、Tavily Search、计算器
- **协议**：HTTP + SSE (Server-Sent Events)

## 快速启动

```bash
# 1. 进入目录
cd langchain-typescript

# 2. 安装依赖
pnpm install

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 API 密钥

# 4. 启动服务
pnpm 12-complete-chat-service
```

服务启动后访问：**http://localhost:2024**

## 环境变量配置

```bash
# 大模型 API 密钥（必须）
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1

# 工具 API 密钥（可选）
TAVILY_API_KEY=your_tavily_api_key  # 网络搜索
OPENWEATHER_API_KEY=your_weather_key  # 天气查询

# 服务配置
MODEL_NAME=gpt-4o-mini
PORT=2024
```

## API 端点

### 1. 根路径 - 服务信息

```bash
GET /
```

**响应示例**：
```json
{
  "service": "LangChain Complete Chat Service",
  "version": "1.0.0",
  "endpoints": {
    "POST /api/chat": "标准聊天接口",
    "POST /api/chat/stream": "SSE 流式聊天接口",
    "GET /api/sessions": "获取所有会话",
    "GET /api/sessions/:id": "获取指定会话详情",
    "GET /api/analytics": "获取分析统计数据",
    "GET /api/health": "健康检查"
  },
  "tools": ["get_weather", "calculate", "search_web"]
}
```

### 2. 健康检查

```bash
GET /api/health
```

**响应示例**：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-26T10:00:00.000Z",
  "uptime": 3600.5,
  "memory": {
    "rss": 123456789,
    "heapTotal": 98765432,
    "heapUsed": 87654321
  }
}
```

### 3. 标准聊天接口

```bash
POST /api/chat
Content-Type: application/json

{
  "message": "北京明天的天气怎么样？",
  "session_id": "session_123"  // 可选，不提供则创建新会话
}
```

**响应示例**：
```json
{
  "message": "北京明天有小雨，气温约 18℃，建议带伞 ☔",
  "session_id": "session_1706265600000_abc123",
  "timestamp": "2024-01-26T10:00:00.000Z"
}
```

**cURL 示例**：
```bash
curl -X POST http://localhost:2024/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "北京明天的天气怎么样？"}'
```

### 4. 流式聊天接口（SSE）

```bash
POST /api/chat/stream
Content-Type: application/json

{
  "message": "计算 2 + 3 * 4 的结果",
  "session_id": "session_123"
}
```

**响应格式**（SSE 流）：
```
data: {"content":"计算","type":"message"}

data: {"content":"结果","type":"message"}

data: {"content":"：","type":"message"}

data: {"content":"14","type":"message"}

data: {"content":"","type":"done","session_id":"session_123"}
```

**cURL 示例**：
```bash
curl -X POST http://localhost:2024/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "北京明天的天气怎么样？"}'
```

### 5. 获取所有会话

```bash
GET /api/sessions
```

**响应示例**：
```json
{
  "sessions": [
    {
      "id": "session_1706265600000_abc123",
      "createdAt": "2024-01-26T10:00:00.000Z",
      "updatedAt": "2024-01-26T10:05:00.000Z",
      "messageCount": 5,
      "metadata": {
        "model": "gpt-4o-mini",
        "totalMessages": 5,
        "totalTokens": 1200
      }
    }
  ],
  "total": 1
}
```

### 6. 获取指定会话详情

```bash
GET /api/sessions/:id
```

**响应示例**：
```json
{
  "id": "session_1706265600000_abc123",
  "createdAt": "2024-01-26T10:00:00.000Z",
  "updatedAt": "2024-01-26T10:05:00.000Z",
  "messages": [
    {
      "role": "user",
      "content": "北京明天的天气怎么样？",
      "timestamp": "2024-01-26T10:00:00.000Z",
      "tokens": 20
    },
    {
      "role": "assistant",
      "content": "北京明天有小雨，气温约 18℃，建议带伞 ☔",
      "timestamp": "2024-01-26T10:00:05.000Z",
      "tokens": 25
    }
  ],
  "metadata": {
    "model": "gpt-4o-mini",
    "totalMessages": 2,
    "totalTokens": 45
  }
}
```

### 7. 获取分析统计

```bash
GET /api/analytics
```

**响应示例**：
```json
{
  "totalSessions": 10,
  "totalMessages": 150,
  "totalTokens": 45000,
  "sessionsLast24Hours": 5,
  "averageMessagesPerSession": 15,
  "averageTokensPerSession": 4500
}
```

## 可用工具

### 1. get_weather - 天气查询

查询指定城市的天气预报。

**示例**：
```
用户: 北京明天的天气怎么样？
工具: get_weather(location="Beijing", days=1)
```

### 2. calculate - 数学计算

计算数学表达式。

**示例**：
```
用户: 计算 2 + 3 * 4 的结果
工具: calculate(expression="2 + 3 * 4")
```

### 3. search_web - 网络搜索

搜索网络信息，获取最新资讯。

**示例**：
```
用户: 搜索 LangChain 最新版本
工具: search_web(query="LangChain latest version")
```

## 与 agentchat.vercel.app 对接

### 配置方式

在 agentchat.vercel.app 中配置自定义 API：

1. 进入设置页面
2. 选择 "Custom API"
3. 设置 API 地址：`http://localhost:2024/api/chat/stream`
4. 设置请求头：
   ```json
   {
     "Content-Type": "application/json"
   }
   ```
5. 设置请求体模板：
   ```json
   {
     "message": "{{message}}",
     "session_id": "{{session_id}}"
   }
   ```

### 支持的功能

- ✅ 流式输出
- ✅ 会话管理
- ✅ 工具调用
- ✅ 历史记录
- ✅ 错误处理

## 架构设计

```
┌─────────────────────────────────────────────────────────┐
│                     Express Server                      │
│                    (Port: 2024)                         │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐
│  Chat API    │ │ Session  │ │  Analytics   │
│  (REST/SSE)  │ │ Manager  │ │  API         │
└──────┬───────┘ └────┬─────┘ └──────────────┘
       │              │
       ▼              ▼
┌──────────────────────────────┐
│     LangChain Agent          │
│  ┌────────┐ ┌──────┐ ┌─────┐ │
│  │ Weather│ │ Calc │ │Search│ │
│  │  Tool  │ │ Tool │ │ Tool │ │
│  └────────┘ └──────┘ └─────┘ │
└─────────────┬────────────────┘
              │
              ▼
┌──────────────────────────────┐
│      OpenAI API              │
│   (DeepSeek/GPT-4o)          │
└──────────────────────────────┘
```

## 数据模型

### Message（消息）
```typescript
interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  tokens?: number;
}
```

### Session（会话）
```typescript
interface Session {
  id: string;
  createdAt: string;
  updatedAt: string;
  messages: Message[];
  metadata: {
    model: string;
    totalMessages: number;
    totalTokens: number;
  };
}
```

## 测试示例

### 测试工具调用

```bash
# 天气查询
curl -X POST http://localhost:2024/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "北京明天的天气怎么样？"}'

# 数学计算
curl -X POST http://localhost:2024/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "计算 (2 + 3) * 4"}'

# 网络搜索
curl -X POST http://localhost:2024/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "搜索 LangChain 1.0 的新特性"}'
```

### 测试会话管理

```bash
# 获取所有会话
curl http://localhost:2024/api/sessions

# 获取指定会话详情
curl http://localhost:2024/api/sessions/session_123

# 查看统计数据
curl http://localhost:2024/api/analytics
```

### 测试流式输出

```bash
curl -X POST http://localhost:2024/api/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "请用 3 点说明 LangChain 的优势"}'
```

## 性能优化建议

1. **会话持久化**：使用 Redis 或数据库存储会话
2. **消息压缩**：压缩历史消息减少 token 消耗
3. **缓存策略**：缓存常用查询结果
4. **限流保护**：添加请求频率限制
5. **监控告警**：集成 Prometheus/Grafana

## 扩展功能

可以基于此服务扩展：

- [ ] 用户认证和授权
- [ ] 多租户支持
- [ ] 自定义工具注册
- [ ] Prompt 模板管理
- [ ] 成本追踪和计费
- [ ] 多模型切换
- [ ] WebSocket 支持
- [ ] 文件上传和处理

## 故障排查

### 常见问题

1. **API 密钥错误**
   - 检查 `.env` 文件中的 `OPENAI_API_KEY`
   - 确认 API 密钥有效且有额度

2. **工具调用失败**
   - 检查 `TAVILY_API_KEY` 和 `OPENWEATHER_API_KEY`
   - 确认 API 服务可用

3. **流式输出中断**
   - 检查网络连接稳定性
   - 确认客户端支持 SSE

4. **会话丢失**
   - 当前会话存储在内存中，重启服务会丢失
   - 生产环境建议使用持久化存储

## 相关链接

- [LangChain 文档](https://docs.langchain.com/)
- [Express 文档](https://expressjs.com/)
- [SSE 规范](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [agentchat.vercel.app](https://agentchat.vercel.app/)

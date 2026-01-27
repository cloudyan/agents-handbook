import express from "express";
import { createAgent, tool } from "langchain";
import { HumanMessage, AIMessage } from "@langchain/core/messages";
import { z } from "zod";
import axios from "axios";
import { createModelClient } from "../clients/model";
import dotenv from "dotenv";

dotenv.config({ override: true });

const PORT = process.env.PORT || 2024;
const app = express();

app.use(express.json());

interface Message {
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
  tokens?: number;
}

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

class SessionManager {
  private sessions: Map<string, Session> = new Map();

  createSession(): Session {
    const session: Session = {
      id: this.generateId(),
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messages: [],
      metadata: {
        model: process.env.MODEL_NAME || "gpt-4o-mini",
        totalMessages: 0,
        totalTokens: 0,
      },
    };
    this.sessions.set(session.id, session);
    return session;
  }

  getSession(id: string): Session | undefined {
    return this.sessions.get(id);
  }

  updateSession(id: string, message: Message): Session | undefined {
    const session = this.sessions.get(id);
    if (!session) return undefined;

    session.messages.push(message);
    session.updatedAt = new Date().toISOString();
    session.metadata.totalMessages = session.messages.length;
    session.metadata.totalTokens += message.tokens || 0;
    return session;
  }

  getAllSessions(): Session[] {
    return Array.from(this.sessions.values());
  }

  getAnalytics() {
    const sessions = this.getAllSessions();
    const totalSessions = sessions.length;
    const totalMessages = sessions.reduce((sum, s) => sum + s.messages.length, 0);
    const totalTokens = sessions.reduce((sum, s) => sum + s.metadata.totalTokens, 0);

    const last24Hours = sessions.filter(
      (s) => new Date(s.createdAt) > new Date(Date.now() - 24 * 60 * 60 * 1000)
    );

    return {
      totalSessions,
      totalMessages,
      totalTokens,
      sessionsLast24Hours: last24Hours.length,
      averageMessagesPerSession: totalSessions > 0 ? totalMessages / totalSessions : 0,
      averageTokensPerSession: totalSessions > 0 ? totalTokens / totalSessions : 0,
    };
  }

  private generateId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

const sessionManager = new SessionManager();

const getWeather = tool(
  async (input) => {
    try {
      const { location, days } = input;
      const weatherApiKeyValue = process.env.OPENWEATHER_API_KEY;

      if (!weatherApiKeyValue) {
        throw new Error("OPENWEATHER_API_KEY 环境变量未设置");
      }

      const response = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?q=${location}&appid=${weatherApiKeyValue}&units=metric&cnt=${days * 8}`
      );

      const data = response.data;
      const forecasts = data.list.slice(0, days * 8);

      let result = `${location} 天气预报：\n`;
      forecasts.forEach((item: any) => {
        const date = new Date(item.dt * 1000);
        result += `${date.toLocaleDateString()} ${item.weather[0].description}, 温度: ${item.main.temp}°C\n`;
      });

      return result;
    } catch (error) {
      if (error instanceof Error) {
        return `获取天气失败: ${error.message}`;
      }
      return "获取天气失败";
    }
  },
  {
    name: "get_weather",
    description: "获取指定城市的天气预报，包括温度、天气状况和降雨概率。输入应该是城市的英文名称。",
    schema: z.object({
      location: z.string().describe("城市英文名称，例如 Beijing, Shanghai"),
      days: z.number().default(1).describe("预报天数，默认为1天"),
    }),
  }
);

const calculate = tool(
  async (input) => {
    try {
      const { expression } = input;
      const result = eval(expression);
      return `计算结果：${result}`;
    } catch {
      return "计算错误，请检查表达式";
    }
  },
  {
    name: "calculate",
    description: "计算数学表达式",
    schema: z.object({
      expression: z.string().describe("数学表达式，如 2 + 3 * 4"),
    }),
  }
);

const searchWeb = tool(
  async (input) => {
    try {
      const { query } = input;
      const tavilyApiKey = process.env.TAVILY_API_KEY;

      if (!tavilyApiKey) {
        throw new Error("TAVILY_API_KEY 环境变量未设置");
      }

      const response = await axios.post(
        "https://api.tavily.com/search",
        {
          api_key: tavilyApiKey,
          query,
          max_results: 5,
          search_depth: "basic",
        }
      );

      const results = response.data.results;
      let result = `搜索结果：\n`;
      results.forEach((item: any, index: number) => {
        result += `${index + 1}. ${item.title}\n`;
        result += `   ${item.url}\n`;
        result += `   ${item.content}\n\n`;
      });

      return result;
    } catch (error) {
      if (error instanceof Error) {
        return `搜索失败: ${error.message}`;
      }
      return "搜索失败";
    }
  },
  {
    name: "search_web",
    description: "搜索网络信息，获取最新的资讯和数据",
    schema: z.object({
      query: z.string().describe("搜索关键词"),
    }),
  }
);

const model = createModelClient({ streaming: true });
const systemPrompt = `你是一个智能助手，可以使用工具来帮助用户回答问题。

工具说明：
1. get_weather - 查询天气预报
2. calculate - 数学计算
3. search_web - 网络搜索

请根据用户的问题，决定是否需要调用工具，并给出最终答案。请用中文回答问题。

回答风格：
- 简洁明了
- 条理清晰
- 主动提供帮助
- 适当使用表情符号增强可读性`;

const agent = createAgent({
  model,
  tools: [getWeather, calculate, searchWeb],
  systemPrompt,
});

app.get("/", (_req, res) => {
  res.json({
    service: "LangChain Complete Chat Service",
    version: "1.0.0",
    endpoints: {
      "POST /api/chat": "标准聊天接口",
      "POST /api/chat/stream": "SSE 流式聊天接口",
      "GET /api/sessions": "获取所有会话",
      "GET /api/sessions/:id": "获取指定会话详情",
      "GET /api/analytics": "获取分析统计数据",
      "GET /api/health": "健康检查",
    },
    tools: ["get_weather", "calculate", "search_web"],
  });
});

app.get("/api/health", (_req, res) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
  });
});

app.get("/api/sessions", (_req, res) => {
  const sessions = sessionManager.getAllSessions();
  res.json({
    sessions: sessions.map((s) => ({
      id: s.id,
      createdAt: s.createdAt,
      updatedAt: s.updatedAt,
      messageCount: s.messages.length,
      metadata: s.metadata,
    })),
    total: sessions.length,
  });
});

app.get("/api/sessions/:id", (req, res) => {
  const { id } = req.params;
  const session = sessionManager.getSession(id);

  if (!session) {
    res.status(404).json({ error: "会话不存在" });
    return;
  }

  res.json(session);
});

app.get("/api/analytics", (_req, res) => {
  const analytics = sessionManager.getAnalytics();
  res.json(analytics);
});

app.post("/api/chat", async (req, res) => {
  try {
    const { message, session_id } = req.body;

    if (!message) {
      res.status(400).json({ error: "请提供 message 参数" });
      return;
    }

    let session: Session;
    if (session_id) {
      const existingSession = sessionManager.getSession(session_id);
      if (existingSession) {
        session = existingSession;
      } else {
        session = sessionManager.createSession();
      }
    } else {
      session = sessionManager.createSession();
    }

    const userMessage: Message = {
      role: "user",
      content: message,
      timestamp: new Date().toISOString(),
    };

    sessionManager.updateSession(session.id, userMessage);

    console.log(`\n[${session.id}] 用户: ${message}`);

    const messages = session.messages
      .slice(0, -1)
      .map((msg) =>
        msg.role === "user"
          ? new HumanMessage(msg.content)
          : new AIMessage(msg.content)
      );

    const response = await agent.invoke({
      messages: [...messages, new HumanMessage(message)],
    });

    const answer = response.messages[response.messages.length - 1].content as string;

    const assistantMessage: Message = {
      role: "assistant",
      content: answer,
      timestamp: new Date().toISOString(),
      tokens: answer.length / 4,
    };

    sessionManager.updateSession(session.id, assistantMessage);

    console.log(`[${session.id}] 助手: ${answer.substring(0, 100)}...`);

    res.json({
      message: answer,
      session_id: session.id,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("处理请求时出错:", error);
    res.status(500).json({
      error: "处理请求失败",
      details: error instanceof Error ? error.message : String(error),
    });
  }
});

app.post("/api/chat/stream", async (req, res) => {
  try {
    const { message, session_id } = req.body;

    if (!message) {
      res.status(400).json({ error: "请提供 message 参数" });
      return;
    }

    let session: Session;
    if (session_id) {
      const existingSession = sessionManager.getSession(session_id);
      if (existingSession) {
        session = existingSession;
      } else {
        session = sessionManager.createSession();
      }
    } else {
      session = sessionManager.createSession();
    }

    const userMessage: Message = {
      role: "user",
      content: message,
      timestamp: new Date().toISOString(),
    };

    sessionManager.updateSession(session.id, userMessage);

    console.log(`\n[${session.id}] 用户 (流式): ${message}`);

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("X-Accel-Buffering", "no");

    const messages = session.messages
      .slice(0, -1)
      .map((msg) =>
        msg.role === "user"
          ? new HumanMessage(msg.content)
          : new AIMessage(msg.content)
      );

    const stream = await agent.stream(
      {
        messages: [...messages, new HumanMessage(message)],
      },
      {
        streamMode: "messages",
      }
    );

    let fullResponse = "";

    const extractTokenText = (token: unknown): string | null => {
      if (!token || typeof token !== "object") {
        return null;
      }

      const content = (token as { content?: unknown }).content;
      if (typeof content === "string") {
        return content;
      }

      if (Array.isArray(content)) {
        const text = content
          .map((block) => {
            if (block && typeof block === "object") {
              const value = (block as { text?: unknown }).text;
              return typeof value === "string" ? value : "";
            }
            return "";
          })
          .join("");
        return text.length > 0 ? text : null;
      }

      return null;
    };

    for await (const chunk of stream) {
      const [message] = Array.isArray(chunk) ? chunk : [chunk];
      const text = extractTokenText(message);
      if (typeof text === "string") {
        fullResponse += text;
        res.write(`data: ${JSON.stringify({ content: text, type: "message" })}\n\n`);
      }
    }

    const assistantMessage: Message = {
      role: "assistant",
      content: fullResponse,
      timestamp: new Date().toISOString(),
      tokens: fullResponse.length / 4,
    };

    sessionManager.updateSession(session.id, assistantMessage);

    res.write(
      `data: ${JSON.stringify({
        content: "",
        type: "done",
        session_id: session.id,
      })}\n\n`
    );
    res.end();

    console.log(`[${session.id}] 助手 (流式): ${fullResponse.substring(0, 100)}...`);
  } catch (error) {
    console.error("处理流式请求时出错:", error);
    res.write(
      `data: ${JSON.stringify({
        error: "处理请求失败",
        type: "error",
        details: error instanceof Error ? error.message : String(error),
      })}\n\n`
    );
    res.end();
  }
});

app.listen(PORT, () => {
  console.log("\n12 - 完整聊天服务");
  console.log("=".repeat(60));
  console.log(`服务运行在 http://localhost:${PORT}`);
  console.log("=".repeat(60));
  console.log("\n可用端点:");
  console.log(`  POST   /api/chat         - 标准聊天`);
  console.log(`  POST   /api/chat/stream  - SSE 流式聊天`);
  console.log(`  GET    /api/sessions     - 会话列表`);
  console.log(`  GET    /api/sessions/:id - 会话详情`);
  console.log(`  GET    /api/analytics    - 分析统计`);
  console.log(`  GET    /api/health       - 健康检查`);
  console.log("\n可用工具:");
  console.log("  - get_weather: 查询天气预报");
  console.log("  - calculate: 数学计算");
  console.log("  - search_web: 网络搜索");
  console.log("\n示例请求:");
  console.log(`curl -X POST http://localhost:${PORT}/api/chat \\`);
  console.log('  -H "Content-Type: application/json" \\');
  console.log('  -d \'{"message": "北京明天的天气怎么样？"}\'');
  console.log("\n流式请求:");
  console.log(`curl -X POST http://localhost:${PORT}/api/chat/stream \\`);
  console.log('  -H "Content-Type: application/json" \\');
  console.log('  -H "Accept: text/event-stream" \\');
  console.log('  -d \'{"message": "北京明天的天气怎么样？"}\'');
  console.log("=".repeat(60));
});

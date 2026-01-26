import express from "express";
import axios from "axios";
import { createAgent, tool } from "langchain";
import * as z from "zod";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "./clients/model";

const PORT = process.env.PORT || 4000;

const app = express();

app.use(express.json());

app.get("/", (_req, res) => {
  res.json({
    message: "LangChain Agent API Server (使用 createAgent)",
    endpoints: {
      "/chat": "POST - 与 Agent 对话（支持工具调用）",
      "/chat/stream": "POST - 与 Agent 对话（SSE 流式输出）",
      "/health": "GET - 健康检查",
    },
    tools: ["get_weather", "calculate"],
  });
  return undefined;
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
  return undefined;
});

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

const model = createModelClient({ streaming: true });
const systemPrompt = "你是一个智能助手，可以使用工具来帮助用户回答问题。请根据用户的问题，决定是否需要调用工具，并给出最终答案。请用中文回答问题。";
const agent = createAgent({
  model,
  tools: [getWeather, calculate],
  systemPrompt,
});

app.post("/chat", async (req, res) => {
  try {
    const body = req.body && typeof req.body === "object" ? req.body : {};
    const { message, session_id } = body as {
      message?: string;
      session_id?: string;
    };

    if (!message) {
      res.status(400).json({ error: "请提供 message 参数" });
      return undefined;
    }

    console.log(`\n[${session_id || "anonymous"}] 用户问题: ${message}`);
    console.log("-".repeat(50));

    // old
    // const response = await model.invoke([new HumanMessage(message)]);
    // console.log(`回复: ${response.content}`);


    // agent
    const response = await agent.invoke({
      messages: [new HumanMessage(message)],
    });

    const answer = response.messages[response.messages.length - 1].content;

    console.log(`\n最终回答: ${answer}`);
    console.log("=".repeat(50));

    res.json({
      message: answer,
      timestamp: new Date().toISOString(),
    });
    return undefined;
  } catch (error) {
    console.error("处理请求时出错:", error);
    res.status(500).json({ error: "处理请求失败" });
    return undefined;
  }
});

app.post("/chat/stream", async (req, res) => {
  try {
    const { message, session_id } = req.body;

    if (!message) {
      res.status(400).json({ error: "请提供 message 参数" });
      return undefined;
    }

    console.log(`\n[${session_id || "anonymous"}] 用户问题 (流式): ${message}`);
    console.log("-".repeat(50));

    res.setHeader("Content-Type", "text/event-stream");
    res.setHeader("Cache-Control", "no-cache");
    res.setHeader("Connection", "keep-alive");
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("X-Accel-Buffering", "no");

    const stream = await agent.stream(
      {
        messages: [new HumanMessage(message)],
      },
      {
        streamMode: "messages",
      }
    );

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
        res.write(`data: ${JSON.stringify({ content: text, type: "message" })}\n\n`);
        console.log(`[流式输出] ${text.substring(0, 50)}...`);
      }
    }

    res.write(`data: ${JSON.stringify({ type: "done" })}\n\n`);
    res.end();

    console.log("\n流式输出完成");
    console.log("=".repeat(50));
    return undefined;
  } catch (error) {
    console.error("处理流式请求时出错:", error);
    res.write(`data: ${JSON.stringify({ error: "处理请求失败", type: "error" })}\n\n`);
    res.end();
    return undefined;
  }
});

app.listen(PORT, () => {
  console.log("\nLangChain Agent API Server");
  console.log("=".repeat(50));
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log(`API 文档: http://localhost:${PORT}/`);
  console.log("=".repeat(50));
  console.log("\n可用工具:");
  console.log("  - get_weather: 查询天气预报");
  console.log("  - calculate: 数学计算");

  console.log("\n示例请求:");
  console.log(`curl -X POST http://localhost:${PORT}/chat \\`);
  console.log('  -H "Content-Type: application/json" \\');
  console.log('  -d \'{"message": "北京明天的天气怎么样？"}\'');
  console.log("\nSSE 流式请求:");
  console.log(`curl -X POST http://localhost:${PORT}/chat/stream \\`);
  console.log('  -H "Content-Type: application/json" \\');
  console.log('  -H "Accept: text/event-stream" \\');
  console.log('  -d \'{"message": "北京明天的天气怎么样？"}\'');
  console.log("=".repeat(50));
});

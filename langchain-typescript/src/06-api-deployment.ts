import dotenv from "dotenv";
import express from "express";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "@langchain/core/messages";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

const apiKey = process.env.OPENAI_API_KEY;
const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

if (!apiKey) {
  console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
  process.exit(1);
}

const llm = new ChatOpenAI({
  modelName,
  openAIApiKey: apiKey,
  configuration: { baseURL },
  temperature: 0.7,
});

app.get("/", (req, res) => {
  res.json({
    message: "LangChain TypeScript API Server",
    endpoints: {
      "/chat": "POST - 发送聊天消息",
      "/health": "GET - 健康检查",
    },
  });
});

app.get("/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

app.post("/chat", async (req, res) => {
  try {
    const { message } = req.body;

    if (!message) {
      return res.status(400).json({ error: "请提供 message 参数" });
    }

    console.log(`📤 收到消息: ${message}`);

    const response = await llm.invoke([new HumanMessage(message)]);

    console.log(`📥 回复: ${response.content}`);

    res.json({
      message: response.content,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error("处理请求时出错:", error);
    res.status(500).json({ error: "处理请求失败" });
  }
});

app.listen(PORT, () => {
  console.log("🚀 LangChain TypeScript API Server");
  console.log("=".repeat(50));
  console.log(`📡 服务器运行在 http://localhost:${PORT}`);
  console.log(`📚 API 文档: http://localhost:${PORT}/`);
  console.log("=".repeat(50));
});

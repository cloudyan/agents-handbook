import express from "express";
import { WebSocketServer, WebSocket } from "ws";
import { createServer } from "http";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "../clients/model";
import { fileURLToPath } from "url";
import { dirname, join } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const server = createServer(app);

const PORT = process.env.PORT || 8000;

app.use(express.json());
app.use(express.static(join(__dirname, ".")));

const llm = createModelClient({
  streaming: true,
});

app.get("/health", (_req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

const wss = new WebSocketServer({ server });

interface ChatSession {
  llm: ChatOpenAI;
  messageHistory: { role: string; content: string }[];
}

const chatSessions = new Map<WebSocket, ChatSession>();

async function* streamResponse(
  llm: ChatOpenAI,
  message: string,
  session: ChatSession
): AsyncGenerator<string, void, unknown> {
  session.messageHistory.push({ role: "user", content: message });

  try {
    const messages = [
      ...session.messageHistory.slice(0, -1).map(msg =>
        msg.role === "user" ? new HumanMessage(msg.content) : { role: msg.role as "assistant", content: msg.content }
      ),
      new HumanMessage(message)
    ];

    const stream = await llm.stream(messages);

    let fullResponse = "";
    for await (const chunk of stream) {
      if (chunk.content) {
        const content = chunk.content as string;
        fullResponse += content;
        yield content; // 逐块返回
      }
    }

    session.messageHistory.push({ role: "assistant", content: fullResponse });
  } catch (e) {
    const errorMsg = `\n[错误: ${e instanceof Error ? e.message : String(e)}]`;
    session.messageHistory.push({ role: "assistant", content: errorMsg });
    yield errorMsg;
  }
}

wss.on("connection", (ws: WebSocket) => {
  try {
    const session: ChatSession = {
      llm,
      messageHistory: [],
    };

    chatSessions.set(ws, session);

    console.log(`✓ 客户端已连接`);

    ws.on("message", async (data: Buffer) => {
      const message = data.toString();
      console.log(`收到消息: ${message.slice(0, 50)}...`);

      try {
        for await (const chunk of streamResponse(llm, message, session)) {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(chunk); // 实时推送到客户端
          }
        }

        if (ws.readyState === WebSocket.OPEN) {
          ws.send("[STREAM_END]");
        }
      } catch (e) {
        const errorMsg = `\n[错误: ${e instanceof Error ? e.message : String(e)}]`;
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(errorMsg);
          ws.send("[STREAM_END]");
        }
        console.log(`处理错误: ${e}`);
      }
    });

    ws.on("close", () => {
      console.log(`✗ 客户端断开连接`);
      chatSessions.delete(ws);
    });

    ws.on("error", (error) => {
      console.log(`WebSocket 错误: ${error}`);
    });
  } catch (e) {
    console.log(`初始化错误: ${e}`);
    ws.close();
}
});

server.listen(PORT, () => {
  console.log("10 - 流式输出 + ChatUI");
  console.log("=".repeat(60));
  console.log(`启动服务器...`);
  console.log(`访问: http://localhost:${PORT}`);
  console.log("=".repeat(60));
});

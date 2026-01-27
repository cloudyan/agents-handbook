import axios from "axios";

const API_URL = "http://localhost:2024";

interface Assistant {
  assistant_id: string;
  version: number;
  config: Record<string, unknown>;
  context: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  graph_id: string;
  metadata: Record<string, unknown>;
  name: string;
  description: string | null;
}

interface Thread {
  thread_id: string;
  created_at: string;
  updated_at: string;
  values: {
    messages: Array<{ role: string; content: string }>;
  };
}

async function testLangGraphAPI() {
  console.log("🧪 测试 LangGraph CLI API");
  console.log("=========================\n");

  try {
    const assistants = await searchAssistants();
    const assistantId = assistants[0].assistant_id;
    console.log(`Assistant ID: ${assistantId}\n`);

    await getAssistantInfo(assistantId);

    const thread = await createThread();
    const threadId = thread.thread_id;
    console.log(`Thread ID: ${threadId}\n`);

    await runAgent(assistantId, threadId, "你好，请介绍一下你自己");

    console.log("\n✅ 所有测试通过！");
  } catch (error) {
    console.error("\n❌ 测试失败:", error);
    if (axios.isAxiosError(error)) {
      console.error(`状态码: ${error.response?.status}`);
      console.error(`响应数据:`, error.response?.data);
    }
  }
}

async function searchAssistants(): Promise<Assistant[]> {
  console.log("1️⃣ 搜索 assistants");
  const response = await axios.post(
    `${API_URL}/assistants/search`,
    { query: "" },
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  const assistants = response.data as Assistant[];
  console.log(`找到 ${assistants.length} 个 assistants\n`);
  return assistants;
}

async function getAssistantInfo(assistantId: string): Promise<void> {
  console.log("2️⃣ 获取 assistant 信息");
  const response = await axios.get(`${API_URL}/assistants/${assistantId}`);
  const assistant = response.data as Assistant;
  console.log(JSON.stringify(assistant, null, 2));
  console.log();
}

async function createThread(): Promise<Thread> {
  console.log("3️⃣ 创建线程");
  const response = await axios.post(
    `${API_URL}/threads`,
    {},
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );
  const thread = response.data as Thread;
  console.log(`创建线程成功\n`);
  return thread;
}

async function runAgent(
  assistantId: string,
  threadId: string,
  message: string
): Promise<void> {
  console.log("4️⃣ 创建运行");
  console.log(`发送消息: ${message}\n`);

  const response = await axios.post(
    `${API_URL}/threads/${threadId}/runs/stream`,
    {
      assistant_id: assistantId,
      input: {
        messages: [
          {
            role: "user",
            content: message,
          },
        ],
      },
    },
    {
      headers: {
        "Content-Type": "application/json",
      },
      responseType: "stream",
    }
  );

  console.log("流式响应:");
  console.log("=========================\n");

  await new Promise<void>((resolve, reject) => {
    response.data.on("data", (chunk: Buffer) => {
      const data = chunk.toString();
      const lines = data.split("\n").filter((line) => line.trim());

      for (const line of lines) {
        if (line.startsWith("event:")) {
          const eventType = line.substring(7).trim();
          console.log(`\n事件: ${eventType}`);
        } else if (line.startsWith("data:")) {
          try {
            const jsonData = JSON.parse(line.substring(6).trim());
            console.log("数据:", JSON.stringify(jsonData, null, 2));
          } catch {
            console.log(line.substring(6).trim());
          }
        }
      }
    });

    response.data.on("end", () => {
      console.log("\n=========================");
      console.log("流式响应结束\n");
      resolve();
    });

    response.data.on("error", (error: Error) => {
      reject(error);
    });
  });
}

testLangGraphAPI();

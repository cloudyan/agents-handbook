import axios from "axios";

const API_URL = "http://localhost:2025";

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

async function testAgentComplete() {
  console.log("🧪 测试完整版 Agent Chat 服务");
  console.log("=========================\n");

  try {
    const assistants = await searchAssistants();
    const assistantId = assistants[0].assistant_id;
    console.log(`Assistant ID: ${assistantId}\n`);

    await getAssistantInfo(assistantId);

    const thread = await createThread();
    const threadId = thread.thread_id;
    console.log(`Thread ID: ${threadId}\n`);

    console.log("📝 测试场景 1: 基础对话");
    await runAgent(assistantId, threadId, "你好，请介绍一下你自己");

    console.log("\n📝 测试场景 2: 数学计算");
    await runAgent(assistantId, threadId, "计算 25 * 4 + 10");

    console.log("\n📝 测试场景 3: 获取时间");
    await runAgent(assistantId, threadId, "现在几点了？");

    console.log("\n📝 测试场景 4: 天气查询");
    await runAgent(assistantId, threadId, "北京明天的天气怎么样？");

    console.log("\n📝 测试场景 5: 网络搜索");
    await runAgent(assistantId, threadId, "搜索最新的 AI 新闻");

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

  let assistantResponse = "";

  await new Promise<void>((resolve, reject) => {
    response.data.on("data", (chunk: Buffer) => {
      const data = chunk.toString();
      const lines = data.split("\n").filter((line) => line.trim());

      for (const line of lines) {
        if (line.startsWith("data:")) {
          try {
            const jsonData = JSON.parse(line.substring(6).trim());
            
            if (jsonData.event === "values" && jsonData.data?.messages) {
              const messages = jsonData.data.messages;
              const lastMsg = messages[messages.length - 1];
              
              if (lastMsg) {
                if (lastMsg.tool_calls && lastMsg.tool_calls.length > 0) {
                  console.log("🔧 工具调用:");
                  lastMsg.tool_calls.forEach((call: any) => {
                    console.log(`   - ${call.name}: ${JSON.stringify(call.args)}`);
                  });
                } else if (lastMsg.role === "assistant" && lastMsg.content) {
                  if (!assistantResponse) {
                    console.log("💬 助手回复:");
                    assistantResponse = lastMsg.content;
                    console.log(lastMsg.content);
                  }
                }
              }
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    });

    response.data.on("end", () => {
      resolve();
    });

    response.data.on("error", (error: Error) => {
      reject(error);
    });
  });
}

testAgentComplete();

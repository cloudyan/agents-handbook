import dotenv from "dotenv";
import { ChatOpenAI } from "@langchain/openai";
import { Tool } from "@langchain/core/tools";
import { z } from "zod";
import { AgentExecutor, createReactAgent } from "langchain/agents";
import { pull } from "langchain/hub";
import axios from "axios";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

const apiKey = process.env.OPENAI_API_KEY;
const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";
const weatherApiKey = process.env.OPENWEATHER_API_KEY;

class WeatherTool extends Tool {
  name = "get_weather";
  description = "获取指定城市的天气预报，包括温度、天气状况和降雨概率。输入应该是城市的英文名称。";

  schema = z.object({
    location: z.string().describe("城市英文名称，例如 Beijing, Shanghai"),
    days: z.number().default(1).describe("预报天数，默认为1天"),
  });

  async _call(input: z.infer<typeof this.schema>): Promise<string> {
    try {
      const { location, days } = input;

      if (!weatherApiKey) {
        throw new Error("OPENWEATHER_API_KEY 环境变量未设置");
      }

      const response = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?q=${location}&appid=${weatherApiKey}&units=metric&cnt=${days * 8}`
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
  }
}

async function weatherAgent() {
  console.log("🌤️  天气智能体 - LangChain TypeScript 示例");
  console.log("=".repeat(50));

  if (!apiKey) {
    console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
    process.exit(1);
  }

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const tools = [new WeatherTool()];

  const prompt = await pull("hwchase17/react");

  const agent = await createReactAgent({
    llm,
    tools,
    prompt,
  });

  const agentExecutor = new AgentExecutor({
    agent,
    tools,
    verbose: true,
  });

  const questions = [
    "北京明天的天气怎么样？",
    "上海需要带伞吗？",
  ];

  for (const question of questions) {
    console.log(`\n📤 用户问题: ${question}`);
    console.log("-".repeat(50));

    const result = await agentExecutor.invoke({
      input: question,
    });

    console.log("\n📥 最终回答:");
    console.log(`  ${result.output}`);
    console.log("=".repeat(50));
  }
}

weatherAgent().catch(console.error);

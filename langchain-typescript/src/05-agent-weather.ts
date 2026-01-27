import axios from "axios";
import { createAgent, tool } from "langchain";
import * as z from "zod";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "./clients/model";

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

async function weatherAgent() {
  const model = createModelClient();
  const tools = [getWeather];

  const agent = createAgent({
    model,
    tools,
    systemPrompt: `你是一个专业的天气助手智能体。你能够：

1. 获取指定城市的天气信息
2. 分析天气数据并提供建议
3. 根据天气情况给出穿衣、出行建议

可用工具：
- get_weather: 获取天气数据

工作流程：
1. 理解用户需求
2. 获取相关天气数据
3. 分析数据并提供建议

请用中文回答，保持友好和专业的语调。`,
  });

  const questions = [
    "北京明天的天气怎么样？",
    "上海需要带伞吗？",
  ];

  for (const question of questions) {
    console.log(`\n用户问题: ${question}`);
    console.log("-".repeat(50));

    try {
      const response = await agent.invoke({
        messages: [new HumanMessage(question)],
      });

      const answer = response.messages[response.messages.length - 1].content;
      console.log("最终回答:");
      console.log(`  ${answer}`);
      console.log(`消息流转数量: ${response.messages.length}`);
    } catch (error) {
      console.log("错误:", error instanceof Error ? error.message : String(error));
    }

    console.log("=".repeat(50));
  }
}

weatherAgent().catch(console.error);

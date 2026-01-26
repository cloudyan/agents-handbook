import axios from "axios";
import { tool } from "langchain";
import * as z from "zod";
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

// 天气智能体
async function weatherAgent() {
  const model = createModelClient();
  const modelWithTools = model.bindTools([getWeather]);

  const questions = [
    "北京明天的天气怎么样？",
    "上海需要带伞吗？",
  ];

  for (const question of questions) {
    console.log(`\n用户问题: ${question}`);
    console.log("-".repeat(50));

    const response = await modelWithTools.invoke(question);
    const toolCalls = response.tool_calls || [];

    if (toolCalls.length > 0) {
      for (const tool_call of toolCalls) {
        console.log(`调用工具: ${tool_call.name}`);
        console.log(`参数: ${JSON.stringify(tool_call.args)}`);

        const toolResult = await getWeather.invoke(tool_call.args as any);
        console.log(`工具结果: ${toolResult}`);

        const finalResponse = await modelWithTools.invoke([
          { role: "user", content: question },
          response,
          {
            role: "tool",
            tool_call_id: tool_call.id,
            content: toolResult as any,
          },
        ]);

        console.log("\n最终回答:");
        console.log(`  ${finalResponse.content}`);
      }
    } else {
      console.log("最终回答:");
      console.log(`  ${response.content}`);
    }

    console.log("=".repeat(50));
  }
}

weatherAgent().catch(console.error);

import { tool } from "langchain";
import { z } from "zod";
import axios from "axios";


export const mockGetWeather = tool(
  async (input) => {
    const { location, days = 1 } = input;
    return `模拟天气预报：${location} 未来 ${days} 天的天气晴朗，气温适宜。`;
  },
  {
    name: "mock_get_weather",
    description: "模拟获取指定城市的天气预报。",
    schema: z.object({
      location: z.string().describe("城市名称"),
      days: z.number().default(1).describe("预报天数，默认为1天"),
    }),
  }
)

/**
 * 天气查询工具
 * 获取指定城市的天气预报
 */
export const getWeather = tool(
  async (input) => {
    try {
      const { location, days = 1 } = input;
      const weatherApiKeyValue = process.env.OPENWEATHER_API_KEY;

      if (!weatherApiKeyValue) {
        return "天气查询功能需要配置 OPENWEATHER_API_KEY 环境变量";
      }

      const response = await axios.get(
        `https://api.openweathermap.org/data/2.5/forecast?q=${location}&appid=${weatherApiKeyValue}&units=metric&cnt=${days * 8}`
      );

      const data = response.data;
      const forecasts = data.list.slice(0, days * 8);

      let result = `${location} 天气预报：\n`;
      forecasts.forEach((item: any) => {
        const date = new Date(item.dt * 1000);
        result += `${date.toLocaleDateString()} ${item.weather[0].description}, 温度: ${item.main.temp}°C, 湿度: ${item.main.humidity}%\n`;
      });

      return result;
    } catch (error) {
      if (error instanceof Error) {
        return `获取天气失败: ${error.message}`;
      }
      return "获取天气失败，请检查城市名称和网络连接";
    }
  },
  {
    name: "get_weather",
    description: "获取指定城市的天气预报，包括温度、天气状况和降雨概率。输入应该是城市的英文名称。",
    schema: z.object({
      location: z.string().describe("城市英文名称，例如 Beijing, Shanghai, New York"),
      days: z.number().default(1).describe("预报天数，默认为1天"),
    }),
  }
);

import { tool } from "langchain";
import { z } from "zod";
import axios from "axios";

/**
 * 天气查询工具
 * 获取指定城市的天气预报
 */
export const getWeatherTool = tool(
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

/**
 * 网络搜索工具
 * 搜索网络获取最新信息
 */
export const searchWebTool = tool(
  async (input) => {
    try {
      const { query, maxResults = 5 } = input;
      const tavilyApiKey = process.env.TAVILY_API_KEY;

      if (!tavilyApiKey) {
        return "网络搜索功能需要配置 TAVILY_API_KEY 环境变量";
      }

      const response = await axios.post(
        "https://api.tavily.com/search",
        {
          api_key: tavilyApiKey,
          query,
          max_results: maxResults,
          search_depth: "basic",
        }
      );

      const results = response.data.results;
      let result = `🔍 搜索结果：\n`;
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
      return "搜索失败，请检查网络连接和 API 密钥";
    }
  },
  {
    name: "search_web",
    description: "搜索网络信息，获取最新的资讯和数据。适用于需要实时信息的问题。",
    schema: z.object({
      query: z.string().describe("搜索关键词"),
      maxResults: z.number().default(5).describe("返回结果数量，默认为5"),
    }),
  }
);

/**
 * 数学计算工具
 * 执行数学表达式计算
 */
export const calculateTool = tool(
  async (input) => {
    try {
      const { expression } = input;

      const sanitized = expression.replace(/[^0-9+\-*/().\s]/g, '');
      const result = eval(sanitized);

      return `计算结果：${expression} = ${result}`;
    } catch {
      return "计算错误，请检查表达式格式。支持 +、-、*、/ 和括号";
    }
  },
  {
    name: "calculate",
    description: "计算数学表达式，支持加减乘除和括号",
    schema: z.object({
      expression: z.string().describe("数学表达式，如 2 + 3 * 4 或 (10 + 5) / 3"),
    }),
  }
);

/**
 * 获取当前时间工具
 */
export const getCurrentTimeTool = tool(
  async () => {
    const now = new Date();
    const options: Intl.DateTimeFormatOptions = {
      timeZone: 'Asia/Shanghai',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    };

    return `当前时间：${now.toLocaleString('zh-CN', options)}`;
  },
  {
    name: "get_current_time",
    description: "获取当前的日期和时间",
    schema: z.object({}),
  }
);

/**
 * 所有工具的导出
 */
export const tools = [
  getWeatherTool,
  searchWebTool,
  calculateTool,
  getCurrentTimeTool,
];

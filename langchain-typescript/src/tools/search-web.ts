import { tool } from "langchain";
import { z } from "zod";
import axios from "axios";

/**
 * 网络搜索工具
 * 搜索网络获取最新信息
 */
export const searchWeb = tool(
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

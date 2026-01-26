import { Tool } from "@langchain/core/tools";
import { z } from "zod";
import { tool } from "@langchain/core/tools";

interface TavilySearchResult {
  title: string;
  url: string;
  content: string;
  score: number;
}

interface TavilyResponse {
  answer: string;
  query: string;
  response_time: number;
  images: string[];
  results: TavilySearchResult[];
}

export function createTavilySearchTool(apiKey: string): Tool {
  return tool(
    async (input: { query: string }) => {
      try {
        const response = await fetch("https://api.tavily.com/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            api_key: apiKey,
            query: input.query,
            search_depth: "basic",
            max_results: 5,
            include_answer: true,
            include_images: false,
            include_image_descriptions: false,
            include_raw_content: false,
          }),
        });

        if (!response.ok) {
          throw new Error(`Tavily API error: ${response.status}`);
        }

        const data = await response.json() as TavilyResponse;

        const searchResults = data.results
          .map(
            (result, index) =>
              `${index + 1}. ${result.title}\n   URL: ${result.url}\n   内容: ${result.content.slice(0, 300)}...`
          )
          .join("\n\n");

        return `搜索结果：\n\n${searchResults}\n\nAI 总结：${data.answer || "无总结"}`;
      } catch (error) {
        console.error("Tavily search error:", error);
        return `搜索失败：${error instanceof Error ? error.message : "未知错误"}`;
      }
    },
    {
      name: "tavily_search",
      description: "使用 Tavily API 进行网络搜索，获取最新的信息和技术资料",
      schema: z.object({
        query: z.string().describe("搜索查询关键词"),
      }),
    }
  ) as unknown as Tool;
}

export function createMockSearchTool(): Tool {
  return tool(
    async (input: { query: string }) => {
      const knowledgeBase: Record<string, string> = {
        "快速排序": "快速排序是一种分治算法，平均时间复杂度 O(n log n)，通过选择基准元素分区实现。",
        "Python": "Python 是一种高级编程语言，语法简洁，适合快速开发。",
        "算法": "算法是解决特定问题的一系列明确步骤。",
        "代码优化": "代码优化包括时间复杂度优化、空间复杂度优化、代码可读性提升等。",
        "JavaScript": "JavaScript 是一种动态编程语言，主要用于 Web 开发，支持事件驱动和函数式编程。",
        "React": "React 是一个用于构建用户界面的 JavaScript 库，由 Facebook 开发，采用组件化架构。",
        "Vue": "Vue.js 是一个渐进式 JavaScript 框架，易于上手，支持双向数据绑定和组件化开发。",
        "Node.js": "Node.js 是一个基于 Chrome V8 引擎的 JavaScript 运行时，用于构建服务器端应用。",
        "TypeScript": "TypeScript 是 JavaScript 的超集，添加了静态类型检查，提高代码可维护性。",
      };

      for (const [key, value] of Object.entries(knowledgeBase)) {
        if (input.query.includes(key)) {
          return `找到：${value}`;
        }
      }

      return `关于 '${input.query}' 的搜索结果：建议查阅官方文档和技术博客。`;
    },
    {
      name: "search_database",
      description: "搜索工具（模拟）",
      schema: z.object({
        query: z.string().describe("搜索查询"),
      }),
    }
  ) as unknown as Tool;
}

export function createSearchTool(): Tool {
  const tavilyApiKey = process.env.TAVILY_API_KEY;

  if (
    tavilyApiKey &&
    tavilyApiKey !== "your_tavily_api_key_here" &&
    tavilyApiKey.length > 10
  ) {
    console.log("✓ 使用 Tavily 搜索 API");
    return createTavilySearchTool(tavilyApiKey);
  } else {
    console.log("⚠ Tavily API Key 未配置，使用模拟搜索工具");
    return createMockSearchTool();
  }
}

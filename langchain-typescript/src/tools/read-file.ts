import { tool } from "langchain";
import { z } from "zod";
import fs from "fs/promises";
import { safePath } from "../utils";

/**
 * 读取文件工具
 * 读取指定路径的文件内容
 */
export const readFile= tool(
  async ({
    filePath,
    limit,
  }: {
    filePath: string;
    limit?: number
  }) => {
    console.log(`\n> read_file: ${filePath}`);
    try {
      const fullPath = safePath(filePath);
      const text = await fs.readFile(fullPath, "utf8");
      const lines = text.split("\n");
      if (limit && limit < lines.length) {
        return lines.slice(0, limit).join("\n") + `\n... (还有 ${lines.length - limit} 行)`;
      }
      return text.substring(0, 50000);
    } catch (e: any) {
      return `错误：${e.message}`;
    }
  },
  {
    name: "read_file",
    description: "读取文件内容。返回 UTF-8 文本。",
    schema: z.object({
      filePath: z.string().describe("要读取的文件的路径，例如 /path/to/file.txt"),
      limit: z.number().optional().describe("最大读取行数 (可选)"),
    }),
  }
);

import { tool } from "langchain";
import { z } from "zod";
import fs from "fs/promises";

/**
 * 读取文件工具
 * 读取指定路径的文件内容
 */


export const readFile= tool(
  async ({
    filePath,
  }) => {
    const content = await fs.readFile(filePath, "utf-8");
    console.log(`[工具调用] read_file: ${filePath} - 成功读取 ${content.length} 字符`);
    return `${content}`;
  },
  {
    name: "read_file",
    description: "用此工具来读取文件内容。当用户要求读取文件、查看代码、分析文件内容时，调用此工具。输入文件路径（可以是相对路径或绝对路径）。",
    schema: z.object({
      filePath: z.string().describe("要读取的文件的路径，例如 /path/to/file.txt"),
    }),
  }
);

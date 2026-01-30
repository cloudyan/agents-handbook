import { tool } from "langchain";
import fs from "fs/promises";
import path from "path";
import { z } from "zod";
import { safePath } from "../utils";

/**
 * 写入文件工具
 * 将内容写入指定路径的文件
 */
export const writeFile = tool(
  async ({
    filePath,
    content,
  }: {
    filePath: string;
    content: string;
  }) => {
    console.log(`\n> write_file: ${filePath}`);
    try {
      const fullPath = safePath(filePath);
      await fs.mkdir(path.dirname(fullPath), { recursive: true });
      await fs.writeFile(fullPath, content);
      return `已写入 ${content.length} 字节到 ${filePath}`;
    } catch (err: any) {
      return `错误：${err.message}`;
    }
  },
  {
    name: "write_file",
    description: "将内容写入指定路径的文件。如果文件不存在则创建它。",
    schema: z.object({
      filePath: z.string().describe("要写入的文件的路径，例如 /path/to/file.txt"),
      content: z.string().describe("要写入文件的内容"),
    }),
  }
);


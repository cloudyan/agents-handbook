import { tool } from "langchain";
import { z } from "zod";
import fs from "fs/promises";
import { safePath } from "../utils";

/**
 * 编辑文件工具
 * 编辑指定路径的文件内容
 */
export const editFile = tool(
  async ({
    filePath,
    oldText,
    newText,
  }: {
    filePath: string;
    oldText: string;
    newText: string;
  }) => {
    try {
      const fullPath = safePath(filePath);
      const content = await fs.readFile(fullPath, "utf8");
      if (!content.includes(oldText)) {
        return `错误：在 ${filePath} 中找不到指定的文本`;
      }

      const newContent = content.replace(oldText, newText);
      await fs.writeFile(fullPath, newContent);
      return `已编辑 ${filePath}`;
    } catch (e: any) {
      return `错误：${e.message}`;
    }
  },
  {
    name: "edit_file",
    description: "替换文件中的确切文本。用于精确编辑。",
    schema: z.object({
      filePath: z.string().describe("要编辑的文件的路径，例如 /path/to/file.txt"),
      oldText: z.string().describe("要查找的确切文本"),
      newText: z.string().describe("替换后的文本"),
    }),
  }
);

import { tool } from "langchain";
import { z } from "zod";

export const bash = tool(
  async ({ command }: { command: string }) => {
    const dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"];
    if (dangerous.some(d => command.includes(d))) {
      return "错误：危险命令被阻止";
    }

    console.log(`\n> bash: ${command}`);
    try {
      const execSync = await import("child_process").then((mod) => mod.execSync);

      // 2 分钟超时限制 & 缓冲区10MB
      return execSync(command, {
        encoding: "utf8",
        timeout: 120000,
        maxBuffer: 1024 * 1024 * 10,
      }) as string;
    } catch (e: any) {
      // bash 工具的错误处理
      const stdout = e.stdout ? e.stdout.toString() : "";
      const stderr = e.stderr ? e.stderr.toString() : "";
      const errorMsg = e.message || "";
      // 完整的错误信息，能让大模型理解错误的原因，并尝试自动修正
      return `错误：${stdout}${stderr}${errorMsg}`.substring(0, 50000);
    }
  },
  {
    name: "bash",
    description: "运行 shell 命令。用于：ls、find、grep、git、npm、python 等。",
    schema: z.object({
      command: z.string().describe("要执行的 Bash 命令，例如 ls -la"),
    }),
  }
);

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
      const exec = await import("child_process").then((mod) => mod.exec);
      return new Promise<string>((resolve) => {
        exec(command, (error, stdout, stderr) => {
          if (error) {
            resolve(`错误：${error.message}`);
            return;
          }
          if (stderr) {
            resolve(`标准错误输出：${stderr}`);
            return;
          }
          resolve(stdout);
        });
      });
    } catch (e: any) {
      return `错误：${e.message}`;
    }
  },
  {
    name: "bash",
    description: "运行 shell 命令。用于：ls、find、grep、git、npm、python 等。",
    schema: z.object({
      command: z.string().describe("要执行的 Bash 命令，例如 ls -la"),
    }),
  }
)

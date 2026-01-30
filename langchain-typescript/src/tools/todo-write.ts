import { tool } from "langchain";
import { z } from "zod";


interface TodoItem {
  content: string;
  status: "pending" | "in_progress" | "completed";
  activeForm: string;
}

class TodoManager {
  private items: TodoItem[] = [];

  update(items: TodoItem[]): string {
    let inProgressCount = 0;
    for (const item of items) {
      if (item.status === "in_progress") inProgressCount++;
    }
    if (items.length > 20) throw new Error("最多允许 20 个待办事项");
    if (inProgressCount > 1) throw new Error("同一时间只能有一个任务处于 'in_progress' 状态");

    this.items = items;
    return this.render();
  }

  render(): string {
    if (this.items.length === 0) return "无待办事项。";
    const lines = this.items.map(item => {
      const icon = item.status === "completed" ? "[x]" : item.status === "in_progress" ? "[>]" : "[ ]";
      const suffix = item.status === "in_progress" ? ` <- ${item.activeForm}` : "";
      return `${icon} ${item.content}${suffix}`;
    });
    const completed = this.items.filter(t => t.status === "completed").length;
    lines.push(`\n(${completed}/${this.items.length} 已完成)`);
    return lines.join("\n");
  }
}

const TODO = new TodoManager();

export const todoWrite = tool(
  async ({
    items,
  }: {
    items: TodoItem[]
  }) => {
    try {
      return TODO.update(items as TodoItem[]);
    } catch (e: any) {
      return `错误：${e.message}`;
    }
  },
  {
    name: "todo_write",
    description: "更新任务列表。用于规划和跟踪进度。同一时间只能有一个任务处于 'in_progress' 状态。",
    schema: z.object({
      items: z.array(z.object({
        content: z.string().describe("任务描述"),
        status: z.enum(["pending", "in_progress", "completed"]).describe("任务状态"),
        activeForm: z.string().describe("当前正在进行的动作描述，例如 '正在读取文件'、'正在编写代码'")
      })).describe("待办事项列表"),
    }),
  }
);

import { tool } from "langchain";
import { z } from "zod";
import { SKILLS } from "../skills/loader";

export function createSkillTool() {
  return tool(
    async ({ skill }: { skill: string }) => {
      const content = SKILLS.getSkillContent(skill);
      if (!content) {
        return "错误：未找到技能";
      }
      return `<skill-loaded name="${skill}">
${content}
</skill-loaded>

请按照上述技能指令完成任务。`;
    },
    {
      name: "skill",
      description: `加载特定领域的专业知识。\n可用技能：\n${SKILLS.getDescriptions()}`,
      schema: z.object({
        skill: z.string().describe("要加载的技能名称")
      })
    }
  );
}

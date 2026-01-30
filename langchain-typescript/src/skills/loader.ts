import * as fs from "fs";
import * as path from "path";

const WORKDIR = process.cwd();
const SKILLS_DIR = path.join(WORKDIR, "skills");

export interface Skill {
  name: string;
  description: string;
  body: string;
  dir: string;
}

export class SkillLoader {
  private skills: Record<string, Skill> = {};

  constructor(skillsDir: string = SKILLS_DIR) {
    this.loadSkills(skillsDir);
  }

  private loadSkills(skillsDir: string) {
    if (!fs.existsSync(skillsDir)) return;
    const dirs = fs.readdirSync(skillsDir, { withFileTypes: true }).filter(d => d.isDirectory());
    for (const d of dirs) {
      const skillMd = path.join(skillsDir, d.name, "SKILL.md");
      if (!fs.existsSync(skillMd)) continue;
      const content = fs.readFileSync(skillMd, "utf8");
      const match = content.match(/^---\s*\n(.*?)\n---\s*\n(.*)$/s);
      if (match) {
        const [, frontmatter, body] = match;
        const metadata: Record<string, string> = {};
        frontmatter.split("\n").forEach(line => {
          const [k, ...v] = line.split(":");
          if (k && v.length) metadata[k.trim()] = v.join(":").trim().replace(/^["']|["']$/g, "");
        });
        if (metadata.name && metadata.description) {
          this.skills[metadata.name] = { 
            name: metadata.name, 
            description: metadata.description, 
            body: body.trim(), 
            dir: path.dirname(skillMd) 
          };
        }
      }
    }
  }

  getDescriptions(): string {
    return Object.entries(this.skills)
      .map(([n, s]) => `- ${n}: ${s.description}`)
      .join("\n") || "(无可用技能)";
  }

  getSkillContent(name: string): string | null {
    const s = this.skills[name];
    if (!s) return null;
    let res = `# 技能: ${s.name}\n\n${s.body}`;
    const folders = [
      { folder: "scripts", label: "脚本" },
      { folder: "references", label: "参考资料" },
      { folder: "assets", label: "资源" }
    ];
    folders.forEach(({ folder, label }) => {
      const fp = path.join(s.dir, folder);
      if (fs.existsSync(fp)) {
        const files = fs.readdirSync(fp);
        if (files.length) res += `\n\n**${s.dir} 中可用的${label}**:\n- ${files.join(", ")}`;
      }
    });
    return res;
  }

  listSkills(): string[] { 
    return Object.keys(this.skills); 
  }
}

export const SKILLS = new SkillLoader();

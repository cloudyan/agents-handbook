import { ChatOpenAI } from "@langchain/openai";
import { Tool } from "@langchain/core/tools";
import { AgentMessage } from "../types";

export class BaseAgent {
  name: string;
  role: string;
  llm: ChatOpenAI;
  tools: Tool[];
  messageHistory: AgentMessage[] = [];

  constructor(name: string, role: string, llm: ChatOpenAI, tools: Tool[] = []) {
    this.name = name;
    this.role = role;
    this.llm = llm;
    this.tools = tools;
  }

  async receiveMessage(message: AgentMessage): Promise<AgentMessage | null> {
    this.messageHistory.push(message);
    return this.processMessage(message);
  }

  async processMessage(_message: AgentMessage): Promise<AgentMessage | null> {
    throw new Error("子类必须实现 processMessage 方法");
  }

  sendMessage(receiver: string, content: string): AgentMessage {
    return {
      sender: this.name,
      receiver,
      content,
    };
  }
}

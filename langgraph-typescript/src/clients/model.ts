import { config } from "dotenv";
import { ChatOpenAI } from "@langchain/openai";

config({ override: true });

export function createModelClient(options?: {
  modelName?: string;
  temperature?: number;
  streaming?: boolean;
}): ChatOpenAI {
  const apiKey = process.env.OPENAI_API_KEY;
  const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
  const modelName = options?.modelName || process.env.MODEL_NAME || "gpt-3.5-turbo";
  const temperature = options?.temperature !== undefined ? options.temperature : 0.7;
  const streaming = options?.streaming ?? false;

  if (!apiKey) {
    throw new Error("请设置 OPENAI_API_KEY 环境变量");
  }

  return new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature,
    streaming,
  });
}

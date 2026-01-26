import { OllamaEmbeddings } from "@langchain/ollama";
import { OpenAIEmbeddings } from "@langchain/openai";
import dotenv from "dotenv";

dotenv.config({ override: true });

export const openAIEmbeddings = (): OpenAIEmbeddings => {
  const apiKey = process.env.OPENAI_API_KEY;
  const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
  const modelName = process.env.EMBEDDING_MODEL_NAME || "text-embedding-ada-002";

if (!apiKey) {
    throw new Error("请设置 OPENAI_API_KEY 环境变量");
  }

  return new OpenAIEmbeddings({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
  });
}

export const ollamaEmbeddings = (): OllamaEmbeddings => {
  return new OllamaEmbeddings({
    model: "nomic-embed-text",  // 或 "mxbai-embed-large"
    baseUrl: "http://localhost:11434",
  });
}

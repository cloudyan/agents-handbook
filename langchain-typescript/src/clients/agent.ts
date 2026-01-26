import { createAgent } from "langchain";
import dotenv from "dotenv";

dotenv.config({ override: true });

export const agent = createAgent({
  model: "openai:gpt-5",
  tools: []
});

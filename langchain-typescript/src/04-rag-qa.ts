import dotenv from "dotenv";
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { OpenAIEmbeddings } from "@langchain/openai";
import axios from "axios";
import * as cheerio from "cheerio";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

async function ragQA() {
  console.log("🔍 检索增强问答 (RAG) - LangChain TypeScript 示例");
  console.log("=".repeat(50));

  const apiKey = process.env.OPENAI_API_KEY;
  const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
  const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

  if (!apiKey) {
    console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
    process.exit(1);
  }

  console.log("\n📥 正在加载文档...");
  const url = "https://docs.langchain.com/docs/introduction";
  const response = await axios.get(url);
  const $ = cheerio.load(response.data);
  const text = $("main").text();

  console.log("✅ 文档加载完成");
  console.log(`📄 文档长度: ${text.length} 字符`);

  console.log("\n🔪 正在分割文档...");
  const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200,
  });

  const chunks = await splitter.splitText(text);
  console.log(`✅ 分割完成，共 ${chunks.length} 个片段`);

  console.log("\n🔤 正在创建向量索引...");
  const embeddings = new OpenAIEmbeddings({
    openAIApiKey: apiKey,
    configuration: { baseURL },
  });

  const vectorStore = await Chroma.fromTexts(chunks, {}, embeddings, {
    collectionName: "langchain-docs",
  });
  console.log("✅ 向量索引创建完成");

  console.log("\n🤖 初始化问答系统...");
  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const prompt = ChatPromptTemplate.fromTemplate(`
请根据以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法回答。

上下文:
{context}

问题: {question}

回答:
`);

  const retriever = vectorStore.asRetriever(3);

  async function ask(question: string): Promise<void> {
    console.log(`\n📤 问题: ${question}`);
    console.log("-".repeat(50));

    const docs = await retriever.invoke(question);
    const context = docs.map((doc) => doc.pageContent).join("\n\n");

    const chain = prompt.pipe(llm);
    const result = await chain.invoke({ context, question });

    console.log(`📥 回答: ${result.content}`);
    console.log(`\n📚 引用了 ${docs.length} 个相关文档片段`);
  }

  await ask("什么是 LangChain？");
  await ask("LangChain 有哪些主要组件？");

  console.log("\n" + "=".repeat(50));
  console.log("✅ RAG 问答系统运行完成！");
}

ragQA().catch(console.error);

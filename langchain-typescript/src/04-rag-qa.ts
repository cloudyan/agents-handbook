import dotenv from "dotenv";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { Chroma } from "@langchain/community/vectorstores/chroma";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { RunnablePassthrough, RunnableSequence } from "@langchain/core/runnables";
import * as cheerio from "cheerio";
import axios from "axios";

import { createModelClient } from "./clients/model";
import { ollamaEmbeddings } from "./clients/embedding";

dotenv.config({ override: true });

// 检索增强问答 (RAG)
async function ragQA() {

  const model = createModelClient({
    temperature: 0,
  });

  console.log("\n准备文档数据...");

  const html = await axios.get("https://docs.langchain.com/oss/python/langchain/overview");
  const $ = cheerio.load(html.data);
  const docs = $("body").text();

  console.log(`文档内容: ${docs}`);
  const allText = Object.values(docs).join("\n\n");

  console.log("文档准备完成");
  console.log(`文档长度: ${allText.length} 字符`);

  console.log("\n🔪 正在分割文档...");
  const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: 500,
    chunkOverlap: 50,
  });

  const chunks = await splitter.splitText(allText);
  console.log(`分割完成，共 ${chunks.length} 个片段`);

  console.log("\n正在创建向量索引...");
  const embeddings = ollamaEmbeddings();
  const vectorStore = await Chroma.fromTexts(
    chunks,
    chunks.map((_, i) => ({ source: "langchain-docs", index: i })),
    embeddings,
    {
      collectionName: "rag-qa-demo",
      clientParams: {
        host: "localhost",
        port: 8000,
      },
    }
  );
  console.log("向量索引创建完成");

  console.log("\n初始化问答系统...");


  const prompt = ChatPromptTemplate.fromTemplate(`
请根据以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法回答。

上下文:
{context}

问题: {question}

回答:
`);

  const retriever = vectorStore.asRetriever(3);

  const formatDocs = (docs: any[]) => {
    return docs.map((doc) => doc.pageContent).join("\n\n");
  };

  const ragChain = RunnableSequence.from([
    {
      context: retriever.pipe(formatDocs),
      question: new RunnablePassthrough(),
    },
    prompt,
    model,
    new StringOutputParser(),
  ]);

  async function ask(question: string): Promise<void> {
    console.log(`\n问题: ${question}`);
    console.log("-".repeat(50));

    const result = await ragChain.invoke(question);

    console.log(`回答: ${result}`);
  }

  await ask("关于 LangChain 你知道什么？");
  await ask("LangChain 提供哪些核心功能？");
  await ask("什么是机器学习？");

  console.log("\n" + "=".repeat(50));
  console.log("RAG 问答系统运行完成！");
}

ragQA().catch(console.error);

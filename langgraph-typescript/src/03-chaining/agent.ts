import { StateGraph, StateSchema, GraphNode, ConditionalEdgeRouter } from "@langchain/langgraph";
import { z } from "zod/v4";
import { createModelClient } from "../clients/model";

const llm = createModelClient();

// Graph state
const State = new StateSchema({
  topic: z.string(),
  joke: z.string(),
  improvedJoke: z.string(),
  finalJoke: z.string(),
});

// 定义节点函数

// 第一次调用LLM生成初始笑话
const generateJoke: GraphNode<typeof State> = async (state) => {
  const msg = await llm.invoke(`写一个关于 ${state.topic} 的短笑话`);
  return { joke: String(msg.content) };
};

// 检查笑话是否有双关语的函数
const checkPunchline = (state: typeof State.State) => {
  // 简单检查 - 笑话中是否包含“?”或“!”
  if (state.joke?.includes("?") || state.joke?.includes("!")) {
    return "Pass";
  }
  return "Fail";
};

// 第二次调用LLM来优化笑话
const improveJoke: GraphNode<typeof State> = async (state) => {
  const msg = await llm.invoke(
    `通过添加文字游戏让这个笑话更有趣：${state.joke}`
  );
  return { improvedJoke: String(msg.content) };
};

// 第三次LLM调用用于最终润色
const polishJoke: GraphNode<typeof State> = async (state) => {
  const msg = await llm.invoke(
    `为这个笑话增加一个令人惊讶的反转：${state.improvedJoke}`
  );
  return { finalJoke: String(msg.content) };
};

//构建 workflow
const chain = new StateGraph(State)
  .addNode("generateJoke", generateJoke)
  .addNode("improveJoke", improveJoke)
  .addNode("polishJoke", polishJoke)
  .addEdge("__start__", "generateJoke")
  .addConditionalEdges("generateJoke", checkPunchline, {
    Pass: "improveJoke",
    Fail: "__end__"
  })
  .addEdge("improveJoke", "polishJoke")
  .addEdge("polishJoke", "__end__")
  .compile();


// Invoke
const state = await chain.invoke({ topic: "cats" });
console.log("初始笑话：");
console.log(state.joke);
console.log("\n--- --- ---\n");
if (state.improvedJoke !== undefined) {
  console.log("改进后的笑话：");
  console.log(state.improvedJoke);
  console.log("\n--- --- ---\n");

  console.log("最终笑话：");
  console.log(state.finalJoke);
} else {
  console.log("笑话未通过质量检查 - 未检测到笑点！");
}

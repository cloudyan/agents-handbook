import * as z from "zod";
import { StateGraph, START, END, Command, GraphNode, interrupt, MemorySaver, StateSchema } from "@langchain/langgraph";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "../clients/model";

const llm = createModelClient();

const EmailClassificationSchema = z.object({
  intent: z.enum(["question", "bug", "billing", "feature", "complex"]),
  urgency: z.enum(["low", "medium", "high", "critical"]),
  topic: z.string(),
  summary: z.string(),
});

const EmailAgentState = new StateSchema({
  emailContent: z.string(),
  senderEmail: z.string(),
  emailId: z.string(),
  classification: EmailClassificationSchema.optional(),
  searchResults: z.array(z.string()).optional(),
  customerHistory: z.record(z.string(), z.any()).optional(),
  responseText: z.string().optional(),
});

type EmailAgentStateType = z.infer<typeof EmailAgentState>;
type EmailClassificationType = z.infer<typeof EmailClassificationSchema>;


const readEmail: GraphNode<typeof EmailAgentState> = async (state, config) => {
  console.log(`正在处理邮件: ${state.emailContent}`);
  return {};
};

const classifyIntent: GraphNode<typeof EmailAgentState> = async (state, config) => {
  const structuredLlm = llm.withStructuredOutput(EmailClassificationSchema);

  const classificationPrompt = `
  请分析以下客户邮件并进行分类：

  邮件内容: ${state.emailContent}
  发件人: ${state.senderEmail}

  请提供分类，包括意图、紧急程度、主题和摘要。
  `;

  const classification = await structuredLlm.invoke(classificationPrompt);

  let nextNode: "searchDocumentation" | "draftResponse" | "bugTracking";

  if (classification.intent === "question" || classification.intent === "feature") {
    nextNode = "searchDocumentation";
  } else if (classification.intent === "bug") {
    nextNode = "bugTracking";
  } else {
    nextNode = "draftResponse";
  }

  return new Command({
    update: { classification },
    goto: nextNode,
  });
};

const searchDocumentation: GraphNode<typeof EmailAgentState> = async (state, config) => {
  const classification = state.classification!;
  const query = `${classification.intent} ${classification.topic}`;

  let searchResults: string[];

  try {
    searchResults = [
      "通过 设置 > 安全 > 修改密码 重置密码",
      "密码必须至少12个字符",
      "包含大写字母、小写字母、数字和符号",
    ];
  } catch (error) {
    searchResults = [`搜索暂时不可用: ${error}`];
  }

  return new Command({
    update: { searchResults },
    goto: "draftResponse",
  });
};

const bugTracking: GraphNode<typeof EmailAgentState> = async (state, config) => {
  const ticketId = "BUG-12345";

  return new Command({
    update: { searchResults: [`已创建 Bug 工单 ${ticketId}`] },
    goto: "draftResponse",
  });
};

const draftResponse: GraphNode<typeof EmailAgentState> = async (state, config) => {
  const classification = state.classification!;

  const contextSections: string[] = [];

  if (state.searchResults) {
    const formattedDocs = state.searchResults.map(doc => `- ${doc}`).join("\n");
    contextSections.push(`相关文档:\n${formattedDocs}`);
  }

  if (state.customerHistory) {
    contextSections.push(`客户等级: ${state.customerHistory.tier ?? "标准"}`);
  }

  const draftPrompt = `
  请为以下客户邮件起草回复:
  ${state.emailContent}

  邮件意图: ${classification.intent}
  紧急程度: ${classification.urgency}

  ${contextSections.join("\n\n")}

  指导原则:
  - 保持专业和乐于助人的态度
  - 针对他们的具体问题
  - 在相关时使用提供的文档
  `;

  const response = await llm.invoke([new HumanMessage(draftPrompt)]);

  const needsReview = (
    classification.urgency === "high" ||
    classification.urgency === "critical" ||
    classification.intent === "complex"
  );

  const nextNode = needsReview ? "humanReview" : "sendReply";

  return new Command({
    update: { responseText: response.content.toString() },
    goto: nextNode,
  });
};

const humanReview: GraphNode<typeof EmailAgentState> = async (state, config) => {
  const classification = state.classification!;

  const humanDecision = interrupt({
    emailId: state.emailId,
    originalEmail: state.emailContent,
    draftResponse: state.responseText,
    urgency: classification.urgency,
    intent: classification.intent,
    action: "请审核并批准/编辑此回复",
  });

  if (humanDecision.approved) {
    return new Command({
      update: { responseText: humanDecision.editedResponse || state.responseText },
      goto: "sendReply",
    });
  } else {
    return new Command({ update: {}, goto: END });
  }
};

const sendReply: GraphNode<typeof EmailAgentState> = async (state, config) => {
  console.log(`正在发送回复: ${state.responseText!.substring(0, 100)}...`);
  return {};
};

const workflow = new StateGraph(EmailAgentState)
  .addNode("readEmail", readEmail)
  .addNode("classifyIntent", classifyIntent, { ends: ["searchDocumentation", "draftResponse", "bugTracking"] })
  .addNode("searchDocumentation", searchDocumentation, { ends: ["draftResponse"] })
  .addNode("bugTracking", bugTracking, { ends: ["draftResponse"] })
  .addNode("draftResponse", draftResponse, { ends: ["humanReview", "sendReply"] })
  .addNode("humanReview", humanReview, { ends: ["sendReply", END] })
  .addNode("sendReply", sendReply)
  .addEdge(START, "readEmail")
  .addEdge("readEmail", "classifyIntent")
  .addEdge("sendReply", END);

const memory = new MemorySaver();
const app = workflow.compile({ checkpointer: memory });

async function runExample() {
  const initialState = {
    emailContent: "我的订阅被扣费两次！这很紧急！",
    senderEmail: "customer@example.com",
    emailId: "email_123"
  };

  const config = { configurable: { thread_id: "customer_123" } };
  const result = await app.invoke(initialState, config);
  console.log(`草稿准备审核: ${result.responseText?.substring(0, 100)}...`);

  const humanResponse = new Command({
    update: {
      responseText: "我们对重复收费深表歉意。我已经立即启动了退款流程..."
    },
    goto: "sendReply"
  });

  const finalResult = await app.invoke(humanResponse, config);
  console.log("邮件发送成功！");
  // console.log(finalResult);
}

runExample().catch(console.error);

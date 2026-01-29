import * as z from "zod";
import {
  StateGraph,
  START,
  END,
  Command,
  GraphNode,
  interrupt,
  MemorySaver,
  StateSchema
} from "@langchain/langgraph";
import { HumanMessage } from "@langchain/core/messages";
import { createModelClient } from "../clients/model";
import type { RetryPolicy } from "@langchain/langgraph";

const llm = createModelClient();

// 定义电子邮件分类结构
const EmailClassificationSchema = z.object({
  intent: z.enum(["question", "bug", "billing", "feature", "complex"]),
  urgency: z.enum(["low", "medium", "high", "critical"]),
  topic: z.string(),
  summary: z.string(),
});

// NOTE: 该状态仅包含原始数据——不包含提示模板、格式化字符串或任何指令。分类输出直接来自 LLM，并以单个字典的形式存储。
const EmailAgentState = new StateSchema({
  // 原始电子邮件数据
  emailContent: z.string(),
  senderEmail: z.string(),
  emailId: z.string(),

  // 分类结果
  classification: EmailClassificationSchema.optional(),

  // 原始搜索结果
  searchResults: z.array(z.string()).optional(),
  customerHistory: z.record(z.string(), z.any()).optional(),

  // 生成内容
  responseText: z.string().optional(),
});

type EmailAgentStateType = z.infer<typeof EmailAgentState>;
type EmailClassificationType = z.infer<typeof EmailClassificationSchema>;


// 模拟工具运行函数
async function runTool(toolCall: string): Promise<string> {
  // 模拟工具执行延迟
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return `工具调用结果: ${toolCall}`;
}

// LLM 可修复
const executeTool: GraphNode<typeof EmailAgentState> = async (state, config) => {
  try {
    const result = await runTool(state.toolCall);
    return new Command({
      update: { toolResult: result },
      goto: "agent",
    });
  } catch (error) {
    // Let the LLM see what went wrong and try again
    return new Command({
      update: { toolResult: `Tool error: ${error}` },
      goto: "agent"
    });
  }
}

// 用户可修复
const lookupCustomerHistory: GraphNode<typeof State> = async (state, config) => {
  if (!state.customerId) {
    const userInput = interrupt({
      message: "Customer ID needed",
      request: "Please provide the customer's account ID to look up their subscription history",
    });
    return new Command({
      update: { customerId: userInput.customerId },
      goto: "lookupCustomerHistory",
    });
  }
  // Now proceed with the lookup
  const customerData = await fetchCustomerHistory(state.customerId);
  return new Command({
    update: { customerHistory: customerData },
    goto: "draftResponse",
  });
}


const readEmail: GraphNode<typeof EmailAgentState> = async (state, config) => {
  // 提取并解析电子邮件内容
  // 在生产环境中，这将连接到您的电子邮件服务
  console.log(`正在处理邮件: ${state.emailContent}`);
  return {};
};

const classifyIntent: GraphNode<typeof EmailAgentState> = async (state, config) => {
  // 使用LLM对邮件意图和紧急程度进行分类，然后相应地路由

  // 创建一个结构化的LLM，返回EmailClassification对象
  const structuredLlm = llm.withStructuredOutput(EmailClassificationSchema);

  // 需要时格式化提示，不存储在状态中
  const classificationPrompt = `
  请分析以下客户邮件并进行分类：

  邮件内容: ${state.emailContent}
  发件人: ${state.senderEmail}

  请提供分类，包括意图、紧急程度、主题和摘要。
  `;

  // 直接获取结构化响应作为对象
  const classification = await structuredLlm.invoke(classificationPrompt);

  // 根据分类确定下一个节点
  let nextNode: "searchDocumentation" | "draftResponse" | "bugTracking";

  if (classification.intent === "question" || classification.intent === "feature") {
    nextNode = "searchDocumentation";
  } else if (classification.intent === "bug") {
    nextNode = "bugTracking";
  } else {
    nextNode = "draftResponse";
  }

  // 将分类存储为状态中的单个对象
  return new Command({
    update: { classification },
    goto: nextNode,
  });
};


const searchDocumentation: GraphNode<typeof EmailAgentState> = async (state, config) => {
  // 在知识库中搜索相关信息

  // 从分类构建搜索查询
  const classification = state.classification!;
  const query = `${classification.intent} ${classification.topic}`;

  let searchResults: string[];

  try {
    // 在此处实现您的搜索逻辑

    // 存储原始搜索结果，而非格式化文本
    searchResults = [
      "通过 设置 > 安全 > 修改密码 重置密码",
      "密码必须至少12个字符",
      "包含大写字母、小写字母、数字和符号",
    ];
  } catch (error) {
    // 对于可恢复的搜索错误，存储错误并继续
    searchResults = [`搜索暂时不可用: ${error}`];
  }

  return new Command({
    update: { searchResults }, // 存储原始结果或错误
    goto: "draftResponse",
  });
};

const bugTracking: GraphNode<typeof EmailAgentState> = async (state, config) => {
  // 创建或更新缺陷跟踪票据

  // 在您的缺陷跟踪系统中创建票据
  const ticketId = "BUG-12345"; // 通过API创建

  return new Command({
    update: { searchResults: [`已创建 Bug 工单 ${ticketId}`] },
    goto: "draftResponse",
  });
};

const draftResponse: GraphNode<typeof EmailAgentState> = async (state, config) => {
  // 根据上下文和路由生成基于质量的响应
  const classification = state.classification!;

  // 根据原始状态数据按需格式化上下文
  const contextSections: string[] = [];

  if (state.searchResults) {
    // 格式化搜索结果以供提示
    const formattedDocs = state.searchResults.map(doc => `- ${doc}`).join("\n");
    contextSections.push(`相关文档:\n${formattedDocs}`);
  }

  if (state.customerHistory) {
    // 格式化客户数据以供提示
    contextSections.push(`客户等级: ${state.customerHistory.tier ?? "标准"}`);
  }

  // 构建带有格式化上下文的提示
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

  // 根据紧急程度和意图确定是否需要人工审核
  const needsReview = (
    classification.urgency === "high" ||
    classification.urgency === "critical" ||
    classification.intent === "complex"
  );

  // 路由到适当的下一个节点
  const nextNode = needsReview ? "humanReview" : "sendReply";

  return new Command({
    update: { responseText: response.content.toString() }, // 仅存储原始响应
    goto: nextNode,
  });
};

const humanReview: GraphNode<typeof EmailAgentState> = async (state, config) => {
  // 暂停以供人工审核，根据决策进行中断和路由
  const classification = state.classification!;

  // interrupt() 必须首先调用 - 在恢复时，它之前的任何代码都将重新运行
  const humanDecision = interrupt({
    emailId: state.emailId,
    originalEmail: state.emailContent,
    draftResponse: state.responseText,
    urgency: classification.urgency,
    intent: classification.intent,
    action: "请审核并批准/编辑此回复",
  });

  // 现在处理人类的决策
  if (humanDecision.approved) {
    return new Command({
      update: { responseText: humanDecision.editedResponse || state.responseText },
      goto: "sendReply",
    });
  } else {
    // 拒绝意味着人类将直接处理
    return new Command({ update: {}, goto: END });
  }
};

// 模拟电子邮件服务
const emailService = {
  async sendEmail({ to, body }: { to: string; body: string; }) {
    // 模拟发送电子邮件的延迟
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log(`电子邮件已发送到 ${to}，内容: ${body.substring(0, 100)}...`);
    return {};
  }
};

const sendReply: GraphNode<typeof EmailAgentState> = async (state, config) => {
  // 发送电子邮件回复

  // 集成电子邮件服务
  try {
    console.log(`正在发送回复: ${state.responseText!.substring(0, 100)}...`);
    return await emailService.sendEmail({
      to: state.senderEmail,
      body: state.responseText!,
    });
  } catch (error) {
    throw new Error(`发送邮件失败: ${error}`);
    // 也可以选择记录错误而不中断工作流
  }
};


// 创建图
// 为了实现人机交互interrupt()，我们需要使用检查点进行编译，以便在运行之间保存状态：
const workflow = new StateGraph(EmailAgentState)
  // 添加节点时进行适当的错误处理
  .addNode("readEmail", readEmail)
  .addNode("classifyIntent", classifyIntent, { ends: ["searchDocumentation", "draftResponse", "bugTracking"] })
  // 为可能发生短暂故障的节点添加重试策略
  .addNode("searchDocumentation", searchDocumentation, {
    // 重试策略：自动重试网络问题和速率限制问题
    retryPolicy: {
      maxAttempts: 3,
      initialInterval: 1.0
    } as RetryPolicy,
    ends: ["draftResponse"]
  })
  .addNode("bugTracking", bugTracking, { ends: ["draftResponse"] })
  .addNode("draftResponse", draftResponse, { ends: ["humanReview", "sendReply"] })
  .addNode("humanReview", humanReview, { ends: ["sendReply", END] })
  .addNode("sendReply", sendReply)
  // 仅保留必要的边缘
  .addEdge(START, "readEmail")
  .addEdge("readEmail", "classifyIntent")
  .addEdge("sendReply", END);

// 使用检查点编译以实现持久化
const memory = new MemorySaver();
const app = workflow.compile({ checkpointer: memory });



// 测试 agent
async function runExample() {
  // 测试紧急账单问题
  const initialState = {
    emailContent: "我的订阅被扣费两次！这很紧急！",
    senderEmail: "customer@example.com",
    emailId: "email_123"
  };

  // 使用thread_id进行持久化运行
  const config = { configurable: { thread_id: "customer_123" } };
  const result = await app.invoke(initialState, config);

  // 图表将在 human_review 处暂停
  console.log(`草稿准备审核: ${result.responseText?.substring(0, 100)}...`);

  // 准备好后，提供人工输入以恢复
  const humanResponse = new Command({
    update: {
      responseText: "我们对重复收费深表歉意。我已经立即启动了退款流程..."
    },
    goto: "sendReply"
  });

  // 恢复执行
  const finalResult = await app.invoke(humanResponse, config);
  console.log("邮件发送成功！");
  // console.log(finalResult);
}

runExample().catch(console.error);

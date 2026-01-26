import dotenv from "dotenv";
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StructuredOutputParser } from "@langchain/core/output_parsers";
import { z } from "zod";

dotenv.config({ override: true });

const apiKey = process.env.OPENAI_API_KEY;
const baseURL = process.env.OPENAI_BASE_URL || "https://api.openai.com/v1";
const modelName = process.env.MODEL_NAME || "gpt-3.5-turbo";

if (!apiKey) {
  console.error("❌ 请设置 OPENAI_API_KEY 环境变量");
  process.exit(1);
}

async function example1BasicExtraction() {
  console.log("\n" + "=".repeat(60));
  console.log("示例 1: 基础信息提取");
  console.log("=".repeat(60));

  const UserInfoSchema = z.object({
    name: z.string().describe("用户姓名"),
    age: z.number().describe("用户年龄").min(0).max(150),
    email: z.string().describe("用户邮箱").email(),
    interests: z.array(z.string()).describe("用户兴趣列表"),
  });

  type UserInfo = z.infer<typeof UserInfoSchema>;

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const parser = StructuredOutputParser.fromZodSchema(UserInfoSchema);

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个信息提取专家，擅长从文本中提取结构化数据。"],
    [
      "user",
      `从以下文本中提取用户信息：
{text}

{format_instructions}`,
    ],
  ]);

  const chain = prompt.pipe(llm).pipe(parser);

  const testText = `
    我叫李明，今年28岁，邮箱是liming@example.com。
    我的兴趣爱好包括编程、阅读和旅行。
  `;

  try {
    const result = await chain.invoke({
      text: testText,
      format_instructions: parser.getFormatInstructions(),
    }) as UserInfo;
    console.log("✓ 提取成功:");
    console.log(JSON.stringify(result, null, 2));
    return result;
  } catch (e) {
    console.log(`✗ 提取失败: ${e}`);
    return null;
  }
}

async function example2NestedModels() {
  console.log("\n" + "=".repeat(60));
  console.log("示例 2: 嵌套模型");
  console.log("=".repeat(60));

  const AddressSchema = z.object({
    street: z.string().describe("街道地址"),
    city: z.string().describe("城市"),
    country: z.string().describe("国家"),
  });

  const CompanySchema = z.object({
    name: z.string().describe("公司名称"),
    industry: z.string().describe("所属行业"),
    address: AddressSchema.describe("公司地址"),
  });

  type Company = z.infer<typeof CompanySchema>;

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const parser = StructuredOutputParser.fromZodSchema(CompanySchema);

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个信息提取专家。"],
    [
      "user",
      `从以下文本中提取公司信息：
{text}

{format_instructions}`,
    ],
  ]);

  const chain = prompt.pipe(llm).pipe(parser);

  const testText = `
    科技创新有限公司是一家专注于人工智能的公司。
    公司位于北京市海淀区中关村大街1号，中国。
  `;

  try {
    const result = await chain.invoke({
      text: testText,
      format_instructions: parser.getFormatInstructions(),
    }) as Company;
    console.log("✓ 提取成功:");
    console.log(JSON.stringify(result, null, 2));
    return result;
  } catch (e) {
    console.log(`✗ 提取失败: ${e}`);
    return null;
  }
}

async function example3EventExtraction() {
  console.log("\n" + "=".repeat(60));
  console.log("示例 3: 事件抽取");
  console.log("=".repeat(60));

  const EventSchema = z.object({
    title: z.string().describe("事件标题"),
    date: z.string().describe("事件日期"),
    location: z.string().describe("事件地点"),
    participants: z.array(z.string()).describe("参与人员"),
    description: z.string().describe("事件描述"),
  });

  type Event = z.infer<typeof EventSchema>;

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const parser = StructuredOutputParser.fromZodSchema(EventSchema);

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个事件信息提取专家。"],
    [
      "user",
      `从以下文本中提取事件信息：
{text}

{format_instructions}`,
    ],
  ]);

  const chain = prompt.pipe(llm).pipe(parser);

  const testText = `
    2024年3月15日，在北京国际会议中心举办了人工智能技术峰会。
    张三、李四、王五等专家参加了会议。
    会议讨论了AI在医疗、教育等领域的应用前景。
  `;

  try {
    const result = await chain.invoke({
      text: testText,
      format_instructions: parser.getFormatInstructions(),
    }) as Event;
    console.log("✓ 提取成功:");
    console.log(JSON.stringify(result, null, 2));
    return result;
  } catch (e) {
    console.log(`✗ 提取失败: ${e}`);
    return null;
  }
}

async function example4ProductExtraction() {
  console.log("\n" + "=".repeat(60));
  console.log("示例 4: 产品信息提取");
  console.log("=".repeat(60));

  const ProductCategoryEnum = z.enum(["电子产品", "服装", "食品", "图书"]);

  const ProductSchema = z.object({
    name: z.string().describe("产品名称"),
    price: z.number().describe("产品价格").min(0),
    category: ProductCategoryEnum.describe("产品类别"),
    description: z.string().optional().describe("产品描述"),
    features: z.array(z.string()).describe("产品特性列表"),
  });

  type Product = z.infer<typeof ProductSchema>;

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const parser = StructuredOutputParser.fromZodSchema(ProductSchema);

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个产品信息提取专家。"],
    [
      "user",
      `从以下文本中提取产品信息：
{text}

{format_instructions}`,
    ],
  ]);

  const chain = prompt.pipe(llm).pipe(parser);

  const testText = `
    智能手机 X200，售价5999元。
    这是一款高性能电子产品，配备6.7英寸OLED屏幕、120Hz刷新率、5000万像素摄像头。
    支持5G网络，续航能力出色。
  `;

  try {
    const result = await chain.invoke({
      text: testText,
      format_instructions: parser.getFormatInstructions(),
    }) as Product;
    console.log("✓ 提取成功:");
    console.log(JSON.stringify(result, null, 2));
    return result;
  } catch (e) {
    console.log(`✗ 提取失败: ${e}`);
    return null;
  }
}

async function example5BatchExtraction() {
  console.log("\n" + "=".repeat(60));
  console.log("示例 5: 批量提取");
  console.log("=".repeat(60));

  const SimpleInfoSchema = z.object({
    name: z.string().describe("名称"),
    value: z.string().describe("值"),
  });

  type SimpleInfo = z.infer<typeof SimpleInfoSchema>;

  const llm = new ChatOpenAI({
    modelName,
    openAIApiKey: apiKey,
    configuration: { baseURL },
    temperature: 0,
  });

  const parser = StructuredOutputParser.fromZodSchema(SimpleInfoSchema);

  const prompt = ChatPromptTemplate.fromMessages([
    ["system", "你是一个信息提取专家。"],
    [
      "user",
      `提取名称和值：
{text}

{format_instructions}`,
    ],
  ]);

  const chain = prompt.pipe(llm).pipe(parser);

  const testTexts = [
    "产品A价格100元",
    "服务B好评率95%",
    "用户C活跃度80",
  ];

  const results: (SimpleInfo | null)[] = [];
  for (let i = 0; i < testTexts.length; i++) {
    try {
      const result = await chain.invoke({
        text: testTexts[i],
        format_instructions: parser.getFormatInstructions(),
      }) as SimpleInfo;
      results.push(result);
      console.log(`✓ 文本 ${i + 1}: ${result.name} = ${result.value}`);
    } catch (e) {
      console.log(`✗ 文本 ${i + 1} 失败: ${e}`);
      results.push(null);
    }
  }

  const successRate = (results.filter((r) => r !== null).length / results.length) * 100;
  console.log(`\n成功率: ${successRate.toFixed(1)}% (${results.filter((r) => r !== null).length}/${results.length})`);
}

async function main() {
  console.log("🦜🔗 08 - 结构化输出");
  console.log("=".repeat(60));

  try {
    await example1BasicExtraction();
    await example2NestedModels();
    await example3EventExtraction();
    await example4ProductExtraction();
    await example5BatchExtraction();

    console.log("\n" + "=".repeat(60));
    console.log("🎉 结构化输出示例运行完成！");
    console.log("=".repeat(60));
    console.log("\n关键要点:");
    console.log("1. 使用 Zod 定义数据模型");
    console.log("2. 使用 StructuredOutputParser 进行解析");
    console.log("3. 添加字段描述和验证规则");
    console.log("4. 处理嵌套模型和复杂类型");
    console.log("5. 批量处理和错误处理");
  } catch (e) {
    console.log(`❌ 运行错误：${e}`);
    process.exit(1);
  }
}

main().catch(console.error);

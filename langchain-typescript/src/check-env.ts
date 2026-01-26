import dotenv from "dotenv";

// 加载环境变量，覆盖已存在的变量
dotenv.config({ override: true });

function checkEnv() {
  console.log("🔍 LangChain TypeScript 环境检查");
  console.log("=".repeat(50));

  console.log("\n🔑 检查环境变量:");
  let hasError = false;

  const openaiKey = process.env.OPENAI_API_KEY;
  if (openaiKey && openaiKey !== "your_openai_api_key_here" && openaiKey.length > 10) {
    console.log("  ✓ OPENAI_API_KEY 已设置");
  } else {
    console.log("  ✗ OPENAI_API_KEY 未设置或无效");
    console.log("  📝 请设置环境变量或创建 .env 文件");
    hasError = true;
  }

  const baseURL = process.env.OPENAI_BASE_URL;
  if (baseURL) {
    console.log(`  ✓ OPENAI_BASE_URL: ${baseURL}`);
  } else {
    console.log("  ℹ OPENAI_BASE_URL 使用默认值");
  }

  const modelName = process.env.MODEL_NAME;
  if (modelName) {
    console.log(`  ✓ MODEL_NAME: ${modelName}`);
  } else {
    console.log("  ℹ MODEL_NAME 使用默认值");
  }

  const tavilyKey = process.env.TAVILY_API_KEY;
  if (tavilyKey && tavilyKey !== "your_tavily_api_key_here" && tavilyKey.length > 10) {
    console.log("  ✓ TAVILY_API_KEY 已设置");
  } else {
    console.log("  ℹ TAVILY_API_KEY 未设置 (搜索功能需要)");
  }

  const openweatherKey = process.env.OPENWEATHER_API_KEY;
  if (openweatherKey && openweatherKey !== "your_openweather_api_key_here" && openweatherKey.length > 10) {
    console.log("  ✓ OPENWEATHER_API_KEY 已设置");
  } else {
    console.log("  ℹ OPENWEATHER_API_KEY 未设置 (天气功能需要)");
  }

  console.log("\n📦 检查 Node.js 版本:");
  const nodeVersion = process.version;
  console.log(`  ${nodeVersion}`);

  console.log("\n" + "=".repeat(50));

  if (hasError) {
    console.log("❌ 环境配置不完整，请检查环境变量");
    process.exit(1);
  }

  console.log("🚀 环境检查通过！可以运行示例:");
  console.log("   pnpm run 01-hello-chain");
  console.log("   pnpm run 05-agent-weather");
}

checkEnv();

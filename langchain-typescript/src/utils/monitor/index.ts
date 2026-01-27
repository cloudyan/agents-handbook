import { promises as fs } from "fs";

export interface PerformanceMetrics {
  chainName: string;
  executionTime: number;
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  success: boolean;
  errorMessage: string;
}

export interface MonitorConfig {
  autoSave?: boolean;
  metricsFile?: string;
  logsFile?: string;
}

export class ProductionMonitor {
  private metricsHistory: PerformanceMetrics[] = [];
  private startTime: number | null = null;
  private config: MonitorConfig;

  constructor(config: MonitorConfig = {}) {
    this.config = {
      autoSave: config.autoSave ?? false,
      metricsFile: config.metricsFile ?? "reports/performance_metrics.json",
      logsFile: config.logsFile ?? "reports/execution_logs.txt",
    };
  }

  startTracking(): void {
    this.startTime = Date.now();
  }

  endTracking(
    chainName: string,
    success: boolean,
    error: string = ""
  ): PerformanceMetrics {
    if (!this.startTime) {
      throw new Error("必须先调用 startTracking()");
    }

    const executionTime = (Date.now() - this.startTime) / 1000;

    const metrics: PerformanceMetrics = {
      chainName,
      executionTime,
      inputTokens: 0,
      outputTokens: 0,
      totalTokens: 0,
      success,
      errorMessage: error,
    };

    this.metricsHistory.push(metrics);
    this.startTime = null;

    if (this.config.autoSave) {
      this.saveMetrics();
    }

    return metrics;
  }

  getSummary(): Record<string, unknown> {
    if (this.metricsHistory.length === 0) {
      return { message: "没有记录的指标" };
    }

    const totalRuns = this.metricsHistory.length;
    const successfulRuns = this.metricsHistory.filter((m) => m.success).length;
    const failedRuns = totalRuns - successfulRuns;

    const avgTime =
      this.metricsHistory.reduce((sum, m) => sum + m.executionTime, 0) / totalRuns;
    const totalTokens = this.metricsHistory.reduce((sum, m) => sum + m.totalTokens, 0);

    return {
      totalRuns,
      successfulRuns,
      failedRuns,
      successRate: successfulRuns / totalRuns,
      averageTime: avgTime,
      totalTokens,
      estimatedCost: totalTokens * 0.00002,
    };
  }

  async saveMetrics(filename?: string): Promise<void> {
    const outputFile = filename || this.config.metricsFile || "metrics.json";
    const data = {
      timestamp: new Date().toISOString(),
      summary: this.getSummary(),
      metrics: this.metricsHistory,
    };

    await fs.writeFile(outputFile, JSON.stringify(data, null, 2), "utf-8");
    console.log(`✓ 指标已保存到 ${outputFile}`);
  }

  getMetrics(): PerformanceMetrics[] {
    return [...this.metricsHistory];
  }

  clearMetrics(): void {
    this.metricsHistory = [];
  }
}

export class CustomLogger {
  private logs: string[] = [];
  private logFile: string;

  constructor(logFile: string = "reports/execution_logs.txt") {
    this.logFile = logFile;
  }

  log(level: string, message: string): void {
    const timestamp = new Date().toLocaleString("zh-CN");
    const logEntry = `[${timestamp}] [${level}] ${message}`;
    this.logs.push(logEntry);
    console.log(logEntry);
  }

  info(message: string): void {
    this.log("INFO", message);
  }

  warn(message: string): void {
    this.log("WARN", message);
  }

  error(message: string): void {
    this.log("ERROR", message);
  }

  debug(message: string): void {
    this.log("DEBUG", message);
  }

  async saveLogs(filename?: string): Promise<void> {
    const outputFile = filename || this.logFile;
    await fs.writeFile(outputFile, this.logs.join("\n"), "utf-8");
    console.log(`✓ 日志已保存到 ${outputFile}`);
  }

  getLogs(): string[] {
    return [...this.logs];
  }

  clearLogs(): void {
    this.logs = [];
  }
}

export function setupLangsmith(): boolean {
  const apiKey = process.env.LANGSMITH_API_KEY || "";
  const tracingEnabled = process.env.LANGSMITH_TRACING === "true";
  const projectName = process.env.LANGSMITH_PROJECT || "agents-handbook";

  if (!apiKey) {
    console.log("⚠️  未设置 LANGSMITH_API_KEY，LangSmith 追踪已禁用");
    console.log("   访问 https://smith.langchain.com/ 获取 API Key");
    return false;
  }

  if (!tracingEnabled) {
    console.log("⚠️  LANGSMITH_TRACING 未设置为 true，LangSmith 追踪已禁用");
    console.log("   在 .env 文件中设置 LANGSMITH_TRACING=true");
    return false;
  }

  // LangChain 会自动读取这些环境变量进行追踪
  console.log("✓ LangSmith 追踪已启用");
  console.log(`  项目名称: ${projectName}`);
  console.log(`  追踪地址: https://smith.langchain.com/`);

  return true;
}

export function createTracer(config?: MonitorConfig) {
  const monitor = new ProductionMonitor(config);
  const logger = new CustomLogger(config?.logsFile);

  return {
    monitor,
    logger,
    langsmithEnabled: setupLangsmith(),
  };
}

export async function withTracking<T>(
  chainName: string,
  monitor: ProductionMonitor,
  logger: CustomLogger,
  fn: () => Promise<T>
): Promise<T> {
  monitor.startTracking();
  try {
    const result = await fn();
    monitor.endTracking(chainName, true);
    return result;
  } catch (e) {
    const errorMessage = e instanceof Error ? e.message : String(e);
    monitor.endTracking(chainName, false, errorMessage);
    logger.error(`${chainName} 错误: ${errorMessage}`);
    throw e;
  }
}

"""性能监控和追踪模块"""
import os
import time
import json
from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass
class PerformanceMetrics:
    """性能指标"""
    chain_name: str
    execution_time: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    success: bool
    error_message: str = ""


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self):
        self.metrics_history = []
        self.start_time = None

    def start_tracking(self):
        """开始追踪"""
        self.start_time = time.time()

    def end_tracking(self, chain_name: str, success: bool, error: str = "") -> PerformanceMetrics:
        """结束追踪并记录指标"""
        if not self.start_time:
            raise ValueError("必须先调用 start_tracking()")

        execution_time = time.time() - self.start_time

        metrics = PerformanceMetrics(
            chain_name=chain_name,
            execution_time=execution_time,
            input_tokens=0,
            output_tokens=0,
            total_tokens=0,
            success=success,
            error_message=error
        )

        self.metrics_history.append(metrics)
        self.start_time = None

        return metrics

    def get_summary(self) -> Dict[str, Any]:
        """获取性能摘要"""
        if not self.metrics_history:
            return {"message": "没有记录的指标"}

        total_runs = len(self.metrics_history)
        successful_runs = sum(1 for m in self.metrics_history if m.success)
        failed_runs = total_runs - successful_runs

        avg_time = sum(m.execution_time for m in self.metrics_history) / total_runs
        total_tokens = sum(m.total_tokens for m in self.metrics_history)

        return {
            "total_runs": total_runs,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": successful_runs / total_runs if total_runs > 0 else 0,
            "average_time": avg_time,
            "total_tokens": total_tokens,
            "estimated_cost": total_tokens * 0.00002,
        }

    def save_metrics(self, filename: str = "reports/performance_metrics.json"):
        """保存指标到文件"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        data = {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_summary(),
            "metrics": [asdict(m) for m in self.metrics_history]
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✓ 指标已保存到 {filename}")


class CustomCallbackHandler:
    """自定义回调处理器"""

    def __init__(self):
        self.logs = []

    def on_llm_start(self, serialized, prompts, **kwargs):
        """LLM 调用开始"""
        self.log("INFO", f"LLM 调用开始: {prompts[0][:50]}...")

    def on_llm_end(self, response, **kwargs):
        """LLM 调用结束"""
        self.log("INFO", "LLM 调用完成")

    def on_llm_error(self, error, **kwargs):
        """LLM 调用错误"""
        self.log("ERROR", f"LLM 错误: {error}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        """Chain 调用开始"""
        chain_name = serialized.get("name", "unknown")
        self.log("INFO", f"Chain '{chain_name}' 开始执行")

    def on_chain_end(self, outputs, **kwargs):
        """Chain 调用结束"""
        self.log("INFO", "Chain 执行完成")

    def on_chain_error(self, error, **kwargs):
        """Chain 调用错误"""
        self.log("ERROR", f"Chain 错误: {error}")

    def on_tool_start(self, serialized, input_str, **kwargs):
        """Tool 调用开始"""
        tool_name = serialized.get("name", "unknown")
        self.log("INFO", f"Tool '{tool_name}' 开始执行: {input_str[:30]}...")

    def on_tool_end(self, output, **kwargs):
        """Tool 调用结束"""
        self.log("INFO", f"Tool 执行完成: {output[:50]}...")

    def on_tool_error(self, error, **kwargs):
        """Tool 调用错误"""
        self.log("ERROR", f"Tool 错误: {error}")

    def log(self, level: str, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        self.logs.append(log_entry)
        print(log_entry)

    def save_logs(self, filename: str = "reports/execution_logs.txt"):
        """保存日志到文件"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(self.logs))

        print(f"✓ 日志已保存到 {filename}")


def setup_langsmith():
    """配置 LangSmith 追踪"""
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️  未设置 LANGSMITH_API_KEY，LangSmith 追踪已禁用")
        print("   访问 https://smith.langchain.com/ 获取 API Key")
        return False

    project_name = os.getenv("LANGSMITH_PROJECT", "agents-handbook")
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGSMITH_PROJECT"] = project_name

    print("✓ LangSmith 追踪已启用")
    print(f"  项目名称: {project_name}")
    print(f"  追踪地址: https://smith.langchain.com/")
    return True

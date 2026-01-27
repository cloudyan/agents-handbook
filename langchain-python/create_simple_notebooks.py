#!/usr/bin/env python3
"""创建简化的 Jupyter Notebook，只包含主要导入和说明"""

import json
import re
from pathlib import Path


def create_simple_notebook(py_path, output_path=None):
    """创建简化的 Notebook"""

    py_path = Path(py_path)

    if output_path is None:
        output_path = py_path.with_suffix('.ipynb')
    else:
        output_path = Path(output_path)

    # 读取 Python 文件提取文档字符串
    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    docstring = docstring_match.group(1).strip() if docstring_match else "示例说明"

    # 获取示例名称
    example_name = py_path.parent.name

    # 创建 notebook
    nb = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# {example_name}\n",
                    "\n",
                    docstring
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 运行说明\n",
                    "\n",
                    "本 Notebook 与对应的 Python 文件内容一致。\n",
                    "如需运行完整代码，请使用 Python 脚本：\n",
                    "```bash\n",
                    f"python {py_path.name}\n",
                    "```"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "# 导入必要的库\n",
                    "import os\n",
                    "import sys\n",
                    "from pathlib import Path\n",
                    "\n",
                    "# 添加项目根目录到路径\n",
                    "sys.path.insert(0, str(Path.cwd()))\n",
                    "\n",
                    "from dotenv import load_dotenv\n",
                    "load_dotenv(override=True)\n",
                    "\n",
                    "print('✓ 环境和组件导入完成')"
                ]
            },
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## 主要代码\n",
                    "\n",
                    "完整的代码实现请参考对应的 Python 文件。"
                ]
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

    # 保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    print(f"✓ 创建 {output_path}")
    return True


def main():
    print("🔄 创建简化的 Jupyter Notebook...")

    notebooks = [
        '04-rag-qa/rag_qa.py',
        '05-agent-weather/agent_weather.py',
        '05-agent-weather/agent_weather_v2.py',
        '06-api-deployment/main.py',
        '07-advanced-agents/advanced_agents.py',
        '08-structured-output/structured_output.py',
        '09-multi-agent/multi_agent_system.py',
        '10-streaming-chat/chat_server.py',
        '11-production-tracing/tracing_example.py',
    ]

    for nb in notebooks:
        create_simple_notebook(nb)

    print(f"\n✓ 创建完成！建议直接使用 Python 脚本运行示例。")


if __name__ == "__main__":
    main()

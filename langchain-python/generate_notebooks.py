#!/usr/bin/env python3
"""从 Python 文件生成 Jupyter Notebook（改进版）"""

import json
import re
import ast
from pathlib import Path


def parse_python_file(py_path):
    """解析 Python 文件，提取结构化信息"""

    with open(py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 提取文档字符串
    docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
    docstring = docstring_match.group(1).strip() if docstring_match else ""

    # 使用 AST 解析代码
    tree = ast.parse(content)

    cells = []

    # 添加文档字符串作为 markdown
    if docstring:
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [docstring]
        })

    # 添加导入单元格
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(f"import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                imports.append(f"from {module} import {alias.name}")

    if imports:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": list(set(imports))  # 去重
        })

    # 提取 main 函数的代码
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'main':
            # 提取函数体
            func_source = ast.get_source_segment(content, node)
            if func_source:
                # 移除函数定义行和缩进
                lines = func_source.split('\n')[1:]  # 跳过 def 行
                # 移除缩进
                dedented_lines = []
                for line in lines:
                    if line.strip():
                        # 计算缩进
                        indent = len(line) - len(line.lstrip())
                        if indent > 0:
                            dedented_lines.append(line[indent:])
                        else:
                            dedented_lines.append(line)
                    else:
                        dedented_lines.append(line)

                # 分割成逻辑单元格
                current_cell = []
                for line in dedented_lines:
                    # 检测 print 语句或注释（作为分隔符）
                    if (line.strip().startswith('print(') or
                        line.strip().startswith('# ===') or
                        line.strip().startswith('print(f"')):
                        if current_cell:
                            cells.append({
                                "cell_type": "code",
                                "execution_count": None,
                                "metadata": {},
                                "outputs": [],
                                "source": current_cell
                            })
                            current_cell = []

                    # 收集代码
                    if line.strip() and not line.strip().startswith('#'):
                        current_cell.append(line)
                    elif current_cell and len(''.join(current_cell)) > 50:
                        # 空行且当前单元格有足够内容
                        cells.append({
                            "cell_type": "code",
                            "execution_count": None,
                            "metadata": {},
                            "outputs": [],
                            "source": current_cell
                        })
                        current_cell = []

                # 添加最后一个单元格
                if current_cell:
                    cells.append({
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": current_cell
                    })

            break

    return cells


def create_notebook_from_py(py_path, output_path=None):
    """从 Python 文件创建 Jupyter Notebook"""

    py_path = Path(py_path)

    if not py_path.exists():
        print(f"⚠️  Python 文件不存在: {py_path}")
        return False

    if output_path is None:
        output_path = py_path.with_suffix('.ipynb')
    else:
        output_path = Path(output_path)

    # 解析 Python 文件
    cells = parse_python_file(py_path)

    # 创建 notebook 结构
    nb = {
        "cells": cells,
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

    # 保存 notebook
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    print(f"✓ 创建 {output_path}")
    return True


def main():
    """主函数"""

    print("🔄 开始生成 Jupyter Notebook 文件...")

    # 需要生成的 notebook 列表
    notebooks_to_create = [
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

    success_count = 0
    for py_path in notebooks_to_create:
        if create_notebook_from_py(py_path):
            success_count += 1

    print(f"\n✓ 成功生成 {success_count}/{len(notebooks_to_create)} 个 Notebook！")
    print("\n提示：使用以下命令打开 Jupyter Lab")
    print("  cd langchain-python")
    print("  jupyter lab")


if __name__ == "__main__":
    main()

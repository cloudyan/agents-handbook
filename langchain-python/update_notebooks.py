#!/usr/bin/env python3
"""更新 Jupyter Notebook 文件，使其与 Python 文件保持一致"""

import json
import re
from pathlib import Path


def update_notebook_from_py(notebook_path, py_path):
    """从 Python 文件更新 Jupyter Notebook"""

    notebook_path = Path(notebook_path)
    py_path = Path(py_path)

    if not py_path.exists():
        print(f"⚠️  Python 文件不存在: {py_path}")
        return

    # 读取 Python 文件
    with open(py_path, 'r', encoding='utf-8') as f:
        py_content = f.read()

    # 读取或创建 Notebook
    if notebook_path.exists():
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    else:
        nb = {"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 4}

    # 提取 Python 文件中的主要部分
    cells = []

    # 提取文档字符串作为 markdown
    docstring_match = re.search(r'"""(.*?)"""', py_content, re.DOTALL)
    if docstring_match:
        docstring = docstring_match.group(1).strip()
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [docstring]
        })

    # 提取导入和初始化部分
    import_section = []
    main_section = []
    in_import = True

    for line in py_content.split('\n'):
        # 跳过文档字符串
        if '"""' in line:
            continue

        # 检测主函数
        if 'def main():' in line:
            in_import = False
            continue

        # 检测函数内的代码
        if line.strip().startswith('def ') or line.strip().startswith('class '):
            if import_section:
                cells.append({
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": import_section
                })
                import_section = []
            continue

        # 跳过 if __name__ == "__main__"
        if '__name__' in line or 'exit(main())' in line:
            continue

        # 收集代码
        if line.strip() and not line.strip().startswith('#'):
            if in_import:
                import_section.append(line)
            else:
                main_section.append(line)

    # 添加导入单元格
    if import_section:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": import_section
        })

    # 添加主代码单元格
    if main_section:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": main_section
        })

    # 更新 notebook
    nb['cells'] = cells

    # 保存
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2, ensure_ascii=False)

    print(f"✓ 更新 {notebook_path}")


def main():
    """主函数"""

    print("🔄 开始更新 Jupyter Notebook 文件...")

    # 需要更新的 notebook 列表
    notebooks_to_update = [
        ('04-rag-qa/rag_qa.ipynb', '04-rag-qa/rag_qa.py'),
        ('05-agent-weather/agent_weather.ipynb', '05-agent-weather/agent_weather.py'),
        ('05-agent-weather/agent_weather_v2.ipynb', '05-agent-weather/agent_weather_v2.py'),
    ]

    for nb_path, py_path in notebooks_to_update:
        update_notebook_from_py(nb_path, py_path)

    print("\n✓ 所有 Notebook 更新完成！")
    print("\n提示：使用 jupyter lab 打开 notebook 查看效果")


if __name__ == "__main__":
    main()

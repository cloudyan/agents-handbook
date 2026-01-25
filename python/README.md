# Python 示例

使用 uv 管理环境和依赖的 LangChain Python 示例集合。

## 快速开始

### 1. 安装 uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 使用 pip 安装
pip install uv
```

### 2. 创建虚拟环境

```bash
cd python
uv venv --python 3.11
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
uv sync
```

### 4. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥
```

### 5. 验证环境

```bash
python 00-env/simple_check.py
```

### 6. 运行示例

```bash
# 使用 Jupyter Lab
jupyter lab 01-hello-chain/

# 直接运行 Python 文件
python 01-hello-chain/hello_chain.py
python 05-agent-weather/agent_weather.py

# 运行 API 服务
python 06-api-deployment/main.py
```

## 开发工具

```bash
# 代码格式化
uv run black .
uv run ruff check --fix .

# 类型检查
uv run mypy .

# 运行测试
uv run pytest
```

## 目录结构

```
python/
├── 00-env/              # 环境验证
├── 01-hello-chain/      # 基础链
├── 02-prompt-template/  # 提示词模板
├── 03-memory-chat/      # 带记忆的对话
├── 04-rag-qa/           # 检索增强问答
├── 05-agent-weather/    # 天气智能体
├── 06-api-deployment/   # API 部署
├── 07-advanced-agents/  # 高级智能体
├── 08-structured-output/ # 结构化输出
├── 09-multi-agent/      # 多智能体协作
├── 10-streaming-chat/   # 流式输出 + ChatUI
├── 11-production-tracing/ # 生产级追踪
├── pyproject.toml       # 项目配置
└── requirements.txt     # 依赖列表
```

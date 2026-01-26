# 开发命令指南

本文档提供所有开发、测试、构建和部署命令的完整说明。

## Python 项目 (langchain-python)

### 环境管理

```bash
# 创建虚拟环境
uv venv --python 3.11

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# 安装依赖
uv sync

# 更新依赖
uv lock --upgrade-package <package-name>
uv sync
```

### 交互式开发

```bash
# 启动 Jupyter Lab（推荐用于学习）
jupyter lab

# 启动特定示例目录
jupyter lab 01-hello-chain/
jupyter lab 04-rag-qa/

# 启动 Jupyter 后台服务
jupyter lab --no-browser --port=8888
```

### 运行示例

```bash
# 环境自检
python 00-env/simple_check.py

# 运行 Python 脚本版本
python 01-hello-chain/hello_chain.py
python 02-prompt-template/prompt_template.py
python 03-memory-chat/memory_chat.py
python 04-rag-qa/rag_qa.py
python 05-agent-weather/agent_weather.py
python 06-api-deployment/main.py
python 07-advanced-agents/advanced_agents.py
python 08-structured-output/structured_output.py
python 09-multi-agent/multi_agent_system.py
python 10-streaming-chat/chat_server.py
python 11-production-tracing/tracing_example.py
```

### 代码质量

```bash
# 格式化代码
uv run black .
uv run black --check .  # 检查格式而不修改

# Lint 检查
uv run ruff check .
uv run ruff check --fix .  # 自动修复可修复的问题

# 同时运行格式化和 lint
uv run black . && uv run ruff check .
```

### 测试

```bash
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest 06-api-deployment/test_api.py

# 运行特定测试函数
uv run pytest 06-api-deployment/test_api.py::test_health

# 详细输出
uv run pytest -v

# 显示覆盖率
uv run pytest --cov=.

# 监听模式（自动重新运行）
uv run pytest --watch
```

### API 部署

```bash
# 启动 FastAPI 服务
cd 06-api-deployment
uv run uvicorn main:app --reload --port 4001

# 后台运行
uv run uvicorn main:app --host 0.0.0.0 --port 4001 --daemon

# 使用 Docker Compose
cd 06-api-deployment
docker-compose up --build
docker-compose down
```

### Docker 操作

```bash
# 构建镜像
docker build -t langchain-python:latest .

# 运行容器
docker run -p 4001:4001 --env-file .env langchain-python:latest

# 使用 Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

## TypeScript 项目 (langchain-typescript)

### 依赖管理

```bash
# 安装依赖
pnpm install

# 添加依赖
pnpm add <package-name>

# 添加开发依赖
pnpm add -D <package-name>

# 更新依赖
pnpm update

# 清理依赖
pnpm store prune
```

### 运行示例

```bash
# 环境验证
pnpm check-env

# 运行示例脚本
pnpm 01-hello-chain
pnpm 02-prompt-template
pnpm 03-memory-chat
pnpm 04-rag-qa
pnpm 05-agent-weather
pnpm 06-api-deployment
pnpm 07-advanced-agents
pnpm 08-structured-output
pnpm 09-multi-agent
pnpm 10-streaming-chat
pnpm 11-production-tracing
```

### 代码质量

```bash
# Lint 检查
pnpm lint
pnpm lint --fix  # 自动修复

# 格式化代码
pnpm format
pnpm format:check  # 检查格式而不修改

# 类型检查
pnpm type-check

# 同时运行所有检查
pnpm lint && pnpm format && pnpm type-check
```

### 构建

```bash
# 构建项目
pnpm build

# 清理构建产物
pnpm clean
```

### API 部署

```bash
# 启动 Express 服务
pnpm 06-api-deployment

# 使用环境变量
NODE_ENV=production pnpm 06-api-deployment

# 后台运行
nohup pnpm 06-api-deployment > server.log 2>&1 &
```

## 环境变量配置

### 创建环境文件

```bash
# 复制模板
cp .env.example .env

# 编辑环境变量
nano .env  # 或使用其他编辑器
```

### 必需的环境变量

```bash
# OpenAI API（或兼容接口）
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com/v1

# 可选：外部服务
TAVILY_API_KEY=your_tavily_key  # 搜索功能
OPENWEATHER_API_KEY=your_weather_key  # 天气查询
```

## 调试技巧

### Python 调试

```bash
# 使用 pdb 调试器
python -m pdb 01-hello-chain/hello_chain.py

# 使用 ipdb（如果已安装）
python -m ipdb 01-hello-chain/hello_chain.py

# Jupyter 调试
# 在 notebook 中使用 %debug 命令
```

### TypeScript 调试

```bash
# 使用 Node.js 调试器
node --inspect-brk src/01-hello-chain.ts

# 使用 tsx 调试
tsx --inspect src/01-hello-chain.ts
```

## 清理和维护

```bash
# Python
rm -rf .venv __pycache__ .pytest_cache
uv cache clean

# TypeScript
rm -rf node_modules dist .next
pnpm store prune

# Git 清理
git clean -fd
git gc
```

## 常见问题排查

### 依赖问题

```bash
# Python
uv lock --rebuild
uv sync --reinstall

# TypeScript
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### 端口占用

```bash
# 查找占用端口的进程
lsof -i :4001  # macOS/Linux
netstat -ano | findstr :4001  # Windows

# 终止进程
kill -9 <PID>
```

### 权限问题

```bash
# macOS/Linux
chmod +x start_jupyter.sh

# Windows（管理员权限运行）
```

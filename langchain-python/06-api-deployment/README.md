# 06 - API Deployment

使用 FastAPI 将天气智能体部署为 HTTP 服务，提供 RESTful API 接口和 SSE 流式输出。

## 文件说明

- `main.py` - FastAPI 应用主文件
- `test_api.py` - API 测试脚本
- `Dockerfile` - Docker 容器配置
- `docker-compose.yml` - Docker Compose 配置

## 快速开始

### 1. 本地运行

```bash
# 进入 langchain-python 目录
cd langchain-python

# 安装依赖（如果还没安装）
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 OPENAI_API_KEY 和 OPENWEATHER_API_KEY

# 启动服务器
uv run python 06-api-deployment/main.py
```

服务器启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 2. Docker 部署

```bash
# 进入目录
cd langchain-python/06-api-deployment

# 构建并运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 测试 API

```bash
# 从 langchain-python 目录运行测试
cd langchain-python
uv run python 06-api-deployment/test_api.py

# 或手动测试
curl http://localhost:8000/health

# 测试对话接口
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "北京明天的天气怎么样？"}'
```

## API 端点

### 基础信息

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 根信息 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | 交互式 API 文档 |
| `/redoc` | GET | ReDoc 文档 |

### 智能体对话

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/chat` | POST | 智能体对话（同步） | JSON Body: ChatRequest |
| `/chat/stream` | POST | 智能体对话（SSE 流式） | JSON Body: ChatRequest |

## 请求/响应格式

### ChatRequest
```json
{
  "message": "北京明天的天气怎么样？",
  "session_id": "user123"
}
```

### ChatResponse
```json
{
  "message": "根据天气数据，明天北京天气晴朗...",
  "timestamp": "2025-01-07T12:00:00"
}
```

### SSE 流式响应
```
data: {"content":"根据","type":"message"}

data: {"content":"天气数据","type":"message"}

data: {"type":"done"}
```

### HealthResponse
```json
{
  "status": "ok",
  "langchain_available": true,
  "openai_configured": true,
  "openweather_configured": true
}
```

## 核心特性

### 1. FastAPI 框架
- 高性能异步框架
- 自动生成 API 文档
- 类型验证和序列化
- 内置错误处理

### 2. LangChain 集成
- 使用 `create_agent` 创建智能体
- 工具调用（get_weather、calculate）
- 自然语言理解
- 上下文感知回复

### 3. 真实天气数据
- 集成 OpenWeather API
- 实时天气信息
- 支持多天预报

### 4. 流式输出
- SSE（Server-Sent Events）支持
- 实时响应
- 改善用户体验

### 5. 部署支持
- Docker 容器化
- Docker Compose 编排
- 环境变量配置
- 生产就绪配置

## 部署架构

### 开发环境
```
客户端 → FastAPI → LangChain Agent → OpenWeather API
```

### 生产环境
```
客户端 → Nginx → FastAPI → Redis 缓存 → LangChain Agent → OpenWeather API
```

## 配置选项

### 环境变量
```bash
OPENAI_API_KEY=sk-xxx                    # OpenAI API 密钥
OPENAI_BASE_URL=https://api.openai.com/v1 # OpenAI API 基础 URL
OPENWEATHER_API_KEY=xxx                   # OpenWeather API 密钥
PORT=8000                                 # 服务端口
```

### FastAPI 配置
```python
app = FastAPI(
    title="LangChain 天气智能体 API",
    description="基于 LangChain 的天气查询和智能建议 API",
    version="1.0.0"
)
```

### CORS 配置
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 性能优化

### 1. 异步处理
- 使用 async/await
- 异步 HTTP 客户端（httpx）
- 非阻塞 I/O

### 2. 缓存策略
- Redis 缓存天气数据
- 智能体响应缓存
- 静态资源缓存

### 3. 负载均衡
- 多实例部署
- Nginx 反向代理
- 健康检查

### 4. 监控和日志
- 结构化日志
- 性能指标
- 错误追踪

## 安全考虑

### 1. 输入验证
- Pydantic 模型验证
- 参数类型检查
- 防止注入攻击

### 2. 访问控制
- API 密钥认证
- 速率限制
- CORS 策略

### 3. 数据保护
- 敏感信息脱敏
- HTTPS 加密
- 日志脱敏

## 测试策略

### 1. 单元测试
```python
def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

### 2. 集成测试
```bash
cd langchain-python
uv run python 06-api-deployment/test_api.py
```

### 3. 性能测试
```bash
# 使用 locust 或 wrk 进行压力测试
wrk -t12 -c400 -d30s http://localhost:8000/health
```

## 生产部署

### 1. 系统要求
- CPU: 2+ 核心
- 内存: 4GB+
- 存储: 20GB+
- 网络: 稳定的互联网连接

### 2. 部署步骤
```bash
# 1. 准备环境
git clone <repository>
cd langchain-python

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 进入部署目录
cd 06-api-deployment

# 4. 构建镜像
docker build -t weather-api .

# 5. 启动服务
docker-compose up -d

# 6. 验证部署
curl http://localhost:8000/health
```

### 3. 监控和维护
- 日志监控
- 性能指标
- 健康检查
- 自动重启

## 环境要求

- Python ≥ 3.11
- uv（包管理工具）
- Docker & Docker Compose（可选）
- OpenAI API 密钥（用于智能体功能）
- OpenWeather API 密钥（用于天气数据）
- 足够的系统资源

## 预期输出

### 服务器启动
```
✓ 智能体初始化完成

🚀 LangChain Agent API Server
==================================================
服务器运行在 http://localhost:8000
API 文档: http://localhost:8000/
==================================================

可用工具:
  - get_weather: 查询天气预报
  - calculate: 数学计算

示例请求:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "北京明天的天气怎么样？"}'

SSE 流式请求:
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "北京明天的天气怎么样？"}'
==================================================
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### API 测试
```
🧪 LangChain 天气智能体 API 测试
==================================================

=== 测试健康检查 ===
状态码：200
服务状态：ok
LangChain 可用：True
OpenAI 配置：True
OpenWeather 配置：True

=== 测试对话 API ===
[anonymous] 用户问题: 北京明天的天气怎么样？
--------------------------------------------------
最终回答: 根据天气数据，明天北京天气晴朗，温度约 18°C，建议适当穿衣。
==================================================

🎉 API 测试完成！
```

## 故障排除

### 常见问题

1. **端口占用**
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   # 终止进程
   kill -9 <PID>
   ```

2. **依赖缺失**
   ```bash
   cd langchain-python
   uv sync
   ```

3. **API 密钥错误**
   ```bash
   # 检查环境变量
   cat .env
   # 重新设置
   # 编辑 .env 文件添加正确的密钥
   ```

4. **Docker 构建失败**
   ```bash
   cd langchain-python/06-api-deployment
   # 清理 Docker 缓存
   docker system prune -a
   # 重新构建
   docker-compose build --no-cache
   ```

5. **智能体初始化失败**
   - 检查 OPENAI_API_KEY 是否正确
   - 检查 OPENAI_BASE_URL 是否可访问
   - 查看错误日志获取详细信息

## 与 TypeScript 版本对应

本实现与 TypeScript 版本保持一致：

| 特性 | Python | TypeScript |
|------|--------|------------|
| 创建 Agent | `create_agent()` | `createAgent()` |
| 工具调用 | `@tool` 装饰器 | `tool()` 函数 |
| 天气 API | OpenWeather | OpenWeather |
| 流式输出 | SSE | SSE |
| 端点 | `/chat`, `/chat/stream` | `/chat`, `/chat/stream` |

## 运行方式说明

### 推荐：从 langchain-python 目录运行
```bash
cd langchain-python
uv run python 06-api-deployment/main.py
uv run python 06-api-deployment/test_api.py
```

### 原因
- 项目使用 uv 统一管理依赖
- 虚拟环境位于 `langchain-python/.venv/`
- 所有依赖在 `pyproject.toml` 中统一配置
- 避免重复安装依赖

### 也可：进入子目录运行
```bash
cd langchain-python/06-api-deployment
# 需要先回到上级目录同步依赖
cd .. && uv sync && cd 06-api-deployment
python main.py
```

## 下一步

完成这个示例后，你已经掌握了：
- LangChain 的核心概念和用法
- 从基础链到复杂智能体的进阶
- RAG 系统的实现
- API 部署和生产化
- 流式输出和实时响应

继续探索：
- 集成更多外部 API
- 添加数据库持久化
- 实现用户认证系统
- 构建前端界面（WebSocket 支持）
- 部署到云平台
- 添加监控和告警

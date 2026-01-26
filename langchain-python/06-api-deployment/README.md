# 06 - API Deployment

使用 FastAPI 将天气智能体部署为 HTTP 服务，提供 RESTful API 接口。

## 文件说明

- `main.py` - FastAPI 应用主文件
- `test_api.py` - API 测试脚本
- `Dockerfile` - Docker 容器配置
- `docker-compose.yml` - Docker Compose 配置

## 快速开始

### 1. 本地运行

```bash
# 进入目录
cd langchain-python/06-api-deployment

# 安装依赖
pip install -r ../../requirements.txt

# 启动服务器
python main.py
```

服务器启动后，访问：
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

### 2. Docker 部署

```bash
# 构建并运行
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 测试 API

```bash
# 运行测试脚本
python test_api.py

# 或手动测试
curl http://localhost:8000/health
curl http://localhost:8000/weather/北京
```

## API 端点

### 基础信息

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 根信息 |
| `/health` | GET | 健康检查 |
| `/docs` | GET | 交互式 API 文档 |
| `/redoc` | GET | ReDoc 文档 |

### 天气查询

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/weather/{location}` | GET | 获取天气信息 | location: 城市名<br>days: 天数(1-7) |
| `/weather` | POST | 获取天气信息 | JSON Body: WeatherRequest |

### 智能体对话

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/chat` | POST | 智能体对话 | JSON Body: ChatRequest |

### 后台任务

| 端点 | 方法 | 描述 | 参数 |
|------|------|------|------|
| `/weather-process/{location}` | POST | 后台处理天气数据 | location: 城市名 |

## 请求/响应格式

### WeatherRequest
```json
{
  "location": "北京",
  "days": 3
}
```

### WeatherResponse
```json
{
  "location": "北京",
  "days": 3,
  "forecast": [
    {
      "date": "2025-01-07",
      "temperature": {
        "min": 15.2,
        "max": 24.8,
        "avg": 20.0
      },
      "condition": "晴",
      "humidity": 45.5,
      "wind_speed": 8.2,
      "rain": false
    }
  ]
}
```

### ChatRequest
```json
{
  "message": "北京明天天气怎么样？",
  "session_id": "user123"
}
```

### ChatResponse
```json
{
  "response": "根据天气数据，明天北京天气晴朗...",
  "session_id": "user123",
  "timestamp": "2025-01-07T12:00:00"
}
```

## 核心特性

### 1. FastAPI 框架
- 高性能异步框架
- 自动生成 API 文档
- 类型验证和序列化
- 内置错误处理

### 2. LangChain 集成
- 智能体工具调用
- 天气数据获取
- 自然语言理解
- 上下文感知回复

### 3. 容错机制
- 优雅降级（无 LangChain 时使用模拟模式）
- 错误处理和日志记录
- 健康检查监控

### 4. 部署支持
- Docker 容器化
- Docker Compose 编排
- 环境变量配置
- 生产就绪配置

## 部署架构

### 开发环境
```
客户端 → FastAPI → LangChain Agent → 天气数据
```

### 生产环境
```
客户端 → Nginx → FastAPI → Redis 缓存 → LangChain Agent → 外部 API
```

## 配置选项

### 环境变量
```bash
OPENAI_API_KEY=sk-xxx                    # OpenAI API 密钥
OPENAI_BASE_URL=https://api.openai.com/v1 # OpenAI API 基础 URL
PYTHONPATH=/app                          # Python 路径
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
- 后台任务处理
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
- SQL 注入防护

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
def test_weather_endpoint():
    response = client.get("/weather/北京")
    assert response.status_code == 200
    assert response.json()["location"] == "北京"
```

### 2. 集成测试
```bash
python test_api.py
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
cd langchain-python/06-api-deployment

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 构建镜像
docker build -t weather-api .

# 4. 启动服务
docker-compose up -d

# 5. 验证部署
curl http://localhost:8000/health
```

### 3. 监控和维护
- 日志监控
- 性能指标
- 健康检查
- 自动重启

## 环境要求

- Python ≥ 3.11
- Docker & Docker Compose（可选）
- OpenAI API 密钥（用于智能体功能）
- 足够的系统资源

## 预期输出

### 服务器启动
```
🚀 启动 LangChain 天气智能体 API 服务
==================================================
API 文档：http://localhost:8000/docs
健康检查：http://localhost:8000/health
天气查询：http://localhost:8000/weather/北京
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### API 测试
```
🧪 LangChain 天气智能体 API 测试
==================================================

=== 测试健康检查 ===
状态码：200
服务状态：healthy
LangChain 可用：True
OpenAI 配置：True

=== 测试天气 API ===
状态码：200
地点：北京
天数：1
天气预报：
  2025-01-07: 15.2-24.8°C, 晴

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
   # 重新安装依赖
   pip install -r ../../requirements.txt
   ```

3. **API 密钥错误**
   ```bash
   # 检查环境变量
   echo $OPENAI_API_KEY
   # 重新设置
   export OPENAI_API_KEY="your-key"
   ```

4. **Docker 构建失败**
   ```bash
   # 清理 Docker 缓存
   docker system prune -a
   # 重新构建
   docker-compose build --no-cache
   ```

## 下一步

完成这个示例后，你已经掌握了：
- LangChain 的核心概念和用法
- 从基础链到复杂智能体的进阶
- RAG 系统的实现
- API 部署和生产化

继续探索：
- 集成真实的外部 API
- 添加数据库持久化
- 实现用户认证系统
- 构建前端界面
- 部署到云平台

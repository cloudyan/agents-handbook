# 00-env 环境配置及验证

在运行 LangChain 示例之前，请先验证环境配置是否正确。

## 使用 uv 管理环境

```bash
# 确保 Python ≥ 3.11
python --version

# 使用 uv 创建虚拟环境并安装依赖
cd python
uv venv --python 3.11
# 3.11 LangChain 官方测试版本，兼容性最好

source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows

# 同步依赖
uv sync

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥

# 运行验证
python 00-env/simple_check.py
```

## 验证内容

- Python 版本检查 (≥ 3.11)
- 核心依赖包安装检查
- 环境变量配置检查 (DEEPSEEK_API_KEY, TAVILY_API_KEY, OPENWEATHER_API_KEY)

# 00-env 环境配置及验证

在运行 LangChain 示例之前，请先验证环境配置是否正确。

## 使用 uv 管理环境

```bash
# 确保 Python ≥ 3.11
python --version

cd langchain-python
# 使用 uv 创建虚拟环境并安装依赖
uv venv --python 3.11
# 也可以指定提示符名称
uv venv --python 3.11 --prompt langchain_311
# 3.11 LangChain 官方测试版本，兼容性最好

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或 .venv\Scripts\activate  # Windows
# 关闭
deactivate

# 同步依赖
uv sync
# 如果项目和缓存目录不同，可以修改，然后同步依赖更快（用 reflink）
uv cache dir
echo 'export UV_CACHE_DIR="/Volumes/data/.cache/uv"' >> ~/.zshrc

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

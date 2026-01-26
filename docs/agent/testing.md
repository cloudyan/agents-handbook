# 测试指南

本文档描述项目的测试基础设施、测试框架和测试约定。

## 测试基础设施概述

### Python 测试

- **测试框架**：pytest
- **测试覆盖**：目前仅 API 部署示例有测试
- **断言库**：pytest 内置断言
- **Mock 库**：pytest-mock（可选）

### TypeScript 测试

- **测试框架**：当前未配置
- **类型检查**：TypeScript 编译器提供静态分析
- **建议框架**：Jest 或 Vitest

## Python 测试

### 当前测试状态

项目目前只有一个测试文件：

```bash
langchain-python/06-api-deployment/test_api.py
```

包含以下测试：
- `test_health()` - 健康检查端点
- `test_weather_api()` - GET 天气查询端点
- `test_weather_post()` - POST 天气查询端点
- `test_chat_api()` - 聊天功能
- `test_background_task()` - 后台任务处理
- `test_error_handling()` - 错误处理

### 运行测试

```bash
# 进入 Python 项目目录
cd langchain-python

# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest 06-api-deployment/test_api.py

# 运行特定测试函数
uv run pytest 06-api-deployment/test_api.py::test_health

# 详细输出
uv run pytest -v

# 显示测试覆盖率
uv run pytest --cov=.

# 监听模式（自动重新运行）
uv run pytest --watch
```

### 测试模式

#### 集成测试模式

当前测试采用集成测试方式：

```python
import pytest
import requests

BASE_URL = "http://localhost:4001"

def test_health():
    """测试健康检查端点"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_weather_api():
    """测试天气查询 API"""
    response = requests.get(
        f"{BASE_URL}/weather",
        params={"location": "Beijing"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "temperature" in data
    assert "description" in data
```

**特点**：
- 测试真实的 HTTP 端点
- 需要先启动 API 服务
- 验证完整的请求-响应流程

#### 错误处理测试

```python
def test_error_handling():
    """测试错误处理"""
    response = requests.get(
        f"{BASE_URL}/weather",
        params={"location": ""}  # 无效参数
    )
    assert response.status_code == 400
    assert "error" in response.json()
```

### 添加新测试

#### 单元测试示例

```python
# tests/test_hello_chain.py
import pytest
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

def test_chain_creation():
    """测试链的创建"""
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个助手"),
        ("user", "{input}")
    ])
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    chain = prompt | llm
    assert chain is not None

def test_chain_invoke():
    """测试链的调用（需要 mock LLM）"""
    from unittest.mock import Mock, patch

    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="测试响应")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个助手"),
        ("user", "{input}")
    ])

    chain = prompt | mock_llm
    result = chain.invoke({"input": "测试"})
    assert result.content == "测试响应"
```

#### RAG 测试示例

```python
# tests/test_rag_qa.py
import pytest
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def test_document_loading():
    """测试文档加载"""
    loader = WebBaseLoader(["https://example.com"])
    docs = loader.load()
    assert len(docs) > 0
    assert docs[0].page_content

def test_text_splitting():
    """测试文本切分"""
    text = "这是一个很长的文本。" * 100
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20
    )
    splits = splitter.split_text(text)
    assert len(splits) > 1
    assert all(len(s) <= 100 for s in splits)
```

### Mock 外部依赖

```python
import pytest
from unittest.mock import Mock, patch

def test_with_mocked_llm():
    """使用 mock LLM 进行测试"""
    with patch('langchain_openai.ChatOpenAI') as mock_llm_class:
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Mock 响应")
        mock_llm_class.return_value = mock_llm

        # 运行测试代码
        result = some_function_using_llm()
        assert result == "Mock 响应"
```

### 测试配置

在 `pyproject.toml` 中配置 pytest：

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

## TypeScript 测试

### 当前状态

TypeScript 项目当前没有配置测试框架。

### 推荐测试框架

#### 使用 Jest

```bash
# 安装 Jest 和相关依赖
pnpm add -D jest @types/jest ts-jest

# 初始化 Jest 配置
pnpm jest --init
```

#### 使用 Vitest（推荐）

```bash
# 安装 Vitest
pnpm add -D vitest @vitest/ui

# 配置 vitest.config.ts
```

### Vitest 配置示例

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import tsconfigPaths from 'vite-tsconfig-paths';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
  plugins: [tsconfigPaths()],
});
```

### 添加 TypeScript 测试

#### 单元测试示例

```typescript
// src/__tests__/hello-chain.test.ts
import { describe, it, expect, vi } from 'vitest';
import { ChatOpenAI } from '@langchain/openai';
import { ChatPromptTemplate } from '@langchain/core/prompts';

describe('Hello Chain', () => {
  it('should create a chain', () => {
    const prompt = ChatPromptTemplate.fromMessages([
      ['system', '你是一个助手'],
      ['user', '{input}']
    ]);

    const llm = new ChatOpenAI({ modelName: 'gpt-3.5-turbo' });
    const chain = prompt.pipe(llm);

    expect(chain).toBeDefined();
  });

  it('should invoke chain with mock', async () => {
    const mockLLM = {
      invoke: vi.fn().mockResolvedValue({
        content: 'Mock 响应'
      })
    };

    const prompt = ChatPromptTemplate.fromMessages([
      ['system', '你是一个助手'],
      ['user', '{input}']
    ]);

    const chain = prompt.pipe(mockLLM as any);
    const result = await chain.invoke({ input: '测试' });

    expect(result.content).toBe('Mock 响应');
    expect(mockLLM.invoke).toHaveBeenCalledTimes(1);
  });
});
```

#### API 测试示例

```typescript
// src/__tests__/api-deployment.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import express from 'express';
import { createApp } from '../06-api-deployment';

describe('API Deployment', () => {
  let app: express.Application;

  beforeAll(() => {
    app = createApp();
  });

  it('should respond to health check', async () => {
    const response = await request(app)
      .get('/health')
      .expect(200);

    expect(response.body.status).toBe('ok');
  });

  it('should handle chat requests', async () => {
    const response = await request(app)
      .post('/chat')
      .send({ message: '你好' })
      .expect(200);

    expect(response.body.response).toBeDefined();
  });
});
```

### 运行 TypeScript 测试

```bash
# 添加测试脚本到 package.json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}

# 运行测试
pnpm test

# 运行带 UI 的测试
pnpm test:ui

# 运行覆盖率测试
pnpm test:coverage
```

## 测试约定

### 文件命名

- **Python**: `test_*.py` 或 `*_test.py`
- **TypeScript**: `*.test.ts` 或 `*.spec.ts`

### 测试位置

```
langchain-python/
├── 01-hello-chain/
│   └── test_hello_chain.py    # 示例内测试
├── 02-prompt-template/
│   └── test_prompt_template.py
├── tests/                     # 集中测试目录
│   ├── test_common.py
│   └── test_utils.py
└── 06-api-deployment/
    └── test_api.py

langchain-typescript/
└── src/
    ├── 01-hello-chain.ts
    ├── 06-api-deployment.ts
    └── __tests__/             # 集中测试目录
        ├── hello-chain.test.ts
        └── api-deployment.test.ts
```

### 测试命名

```python
# Python
def test_function_name():
    """测试描述"""
    pass

class TestClassName:
    def test_method_name(self):
        """测试描述"""
        pass
```

```typescript
// TypeScript
describe('Feature Name', () => {
  it('should do something', () => {
    // 测试代码
  });
});
```

### 测试结构

使用 Given-When-Then 模式：

```python
def test_weather_query():
    """测试天气查询功能"""
    # Given: 设置测试数据
    location = "Beijing"

    # When: 执行操作
    result = get_weather(location)

    # Then: 验证结果
    assert result["location"] == location
    assert "temperature" in result
```

```typescript
it('should query weather', () => {
  // Given
  const location = 'Beijing';

  // When
  const result = getWeather(location);

  // Then
  expect(result.location).toBe(location);
  expect(result.temperature).toBeDefined();
});
```

## 测试最佳实践

### 1. 测试隔离

每个测试应该独立运行：

```python
# ❌ 不好 - 测试之间有依赖
def test_a():
    global.state = "modified"

def test_b():
    assert global.state == "modified"  # 依赖 test_a

# ✅ 好 - 独立测试
def test_a():
    assert something() == "expected"

def test_b():
    assert something_else() == "expected"
```

### 2. 使用 fixtures

```python
@pytest.fixture
def mock_llm():
    """创建 mock LLM 实例"""
    return ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

def test_with_fixture(mock_llm):
    result = mock_llm.invoke("测试")
    assert result is not None
```

### 3. Mock 外部 API

```python
import pytest
from unittest.mock import patch

@pytest.fixture
def mock_openai_api():
    """Mock OpenAI API 调用"""
    with patch('langchain_openai.ChatOpenAI.invoke') as mock:
        mock.return_value = "Mock 响应"
        yield mock
```

### 4. 参数化测试

```python
@pytest.mark.parametrize("location,expected_temp", [
    ("Beijing", 20),
    ("Shanghai", 25),
    ("Guangzhou", 30),
])
def test_weather_in_different_cities(location, expected_temp):
    result = get_weather(location)
    assert result["temperature"] == expected_temp
```

### 5. 异步测试

```python
import pytest

@pytest.mark.asyncio
async def test_async_chain():
    result = await async_chain.invoke({"input": "测试"})
    assert result is not None
```

```typescript
// TypeScript
import { describe, it, expect } from 'vitest';

describe('Async Chain', () => {
  it('should invoke async chain', async () => {
    const result = await asyncChain.invoke({ input: '测试' });
    expect(result).toBeDefined();
  });
});
```

## 测试覆盖率

### Python

```bash
# 生成覆盖率报告
uv run pytest --cov=. --cov-report=html

# 查看报告
open htmlcov/index.html
```

### TypeScript (Vitest)

```bash
# 生成覆盖率报告
pnpm test:coverage

# 查看报告
open coverage/index.html
```

### 覆盖率目标

- **总体覆盖率**：> 80%
- **核心模块**：> 90%
- **示例代码**：> 60%（示例优先考虑可读性）

## 持续集成

### GitHub Actions 示例

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install uv
        run: pip install uv
      - name: Install dependencies
        run: |
          cd langchain-python
          uv sync
      - name: Run tests
        run: |
          cd langchain-python
          uv run pytest --cov=.

  test-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pnpm/action-setup@v2
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: |
          cd langchain-typescript
          pnpm install
      - name: Run tests
        run: |
          cd langchain-typescript
          pnpm test
```

## 测试待办事项

### Python

- [ ] 为每个示例添加单元测试
- [ ] 为核心功能添加集成测试
- [ ] 添加性能测试
- [ ] 配置测试覆盖率报告
- [ ] 添加 CI/CD 集成

### TypeScript

- [ ] 选择并配置测试框架（Vitest 推荐）
- [ ] 为每个示例添加测试
- [ ] 配置类型检查作为测试的一部分
- [ ] 添加覆盖率报告
- [ ] 添加 CI/CD 集成

## 常见问题

### 测试失败

```bash
# 查看详细错误信息
uv run pytest -v -s

# 只运行失败的测试
uv run pytest --lf

# 在第一个失败时停止
uv run pytest -x
```

### 测试超时

```python
@pytest.mark.timeout(10)  # 10 秒超时
def test_slow_operation():
    time.sleep(5)
```

### 并行测试

```python
# pytest-xdist 插件
pip install pytest-xdist

# 并行运行测试
pytest -n auto
```

## 资源链接

- [Pytest 官方文档](https://docs.pytest.org/)
- [Vitest 官方文档](https://vitest.dev/)
- [Testing Best Practices](https://testingjavascript.com/)

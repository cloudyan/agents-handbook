# 08 - 结构化输出

展示如何使用 LangChain 进行结构化数据提取和验证，将 LLM 输出转换为强类型数据。

## 核心概念

### 什么是结构化输出？
```
传统输出：
"用户张三，年龄25岁，邮箱zhangsan@example.com"

结构化输出：
{
  "name": "张三",
  "age": 25,
  "email": "zhangsan@example.com"
}
```

### 为什么需要结构化输出？
1. **数据验证**：确保输出符合预期格式
2. **类型安全**：避免运行时错误
3. **易于处理**：直接对接数据库、API
4. **提高可靠性**：减少解析错误

## 运行方法

```bash
cd langchain-python
python 08-structured-output/structured_output.py
```

## 核心示例

### 1. Pydantic 模型定义
```python
from pydantic import BaseModel, Field

class UserInfo(BaseModel):
    """用户信息模型"""
    name: str = Field(description="用户姓名")
    age: int = Field(description="用户年龄", ge=0, le=150)
    email: str = Field(description="用户邮箱")
    interests: List[str] = Field(description="用户兴趣列表")
```

### 2. 使用 LangChain 提取
```python
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser

llm = ChatOpenAI(model="gpt-3.5-turbo")
parser = PydanticOutputParser(pydantic_object=UserInfo)

prompt = PromptTemplate.from_template(
    "从文本中提取用户信息：\n{text}\n\n{format_instructions}"
)

chain = prompt | llm | parser
result = chain.invoke({"text": user_input})
```

## 应用场景

### 场景 1：用户信息提取
从自然语言文本中提取结构化用户信息

### 场景 2：事件抽取
从新闻文本中提取事件信息（时间、地点、人物）

### 场景 3：产品信息提取
从商品描述中提取产品规格

### 场景 4：表格数据生成
将非结构化文本转换为表格数据

## 高级用法

### 1. 嵌套模型
```python
class Address(BaseModel):
    street: str
    city: str
    country: str

class Person(BaseModel):
    name: str
    address: Address
```

### 2. 可选字段
```python
class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
```

### 3. 枚举类型
```python
from enum import Enum

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(BaseModel):
    title: str
    priority: Priority
```

### 4. 自定义验证
```python
from pydantic import validator

class User(BaseModel):
    email: str

    @validator('email')
    def email_must_contain_at(cls, v):
        if '@' not in v:
            raise ValueError('must contain @')
        return v
```

## 最佳实践

### 1. 清晰的字段描述
```python
# 好的做法
age: int = Field(description="用户年龄，范围0-150")

# 不好的做法
age: int
```

### 2. 合理的验证规则
```python
# 设置范围限制
price: float = Field(description="价格", ge=0)

# 设置长度限制
title: str = Field(description="标题", min_length=1, max_length=100)
```

### 3. 错误处理
```python
try:
    result = chain.invoke({"text": input_text})
except Exception as e:
    print(f"解析错误: {e}")
    # 重试或使用默认值
```

### 4. 批量处理
```python
results = []
for text in texts:
    try:
        result = chain.invoke({"text": text})
        results.append(result)
    except:
        results.append(None)
```

## 性能优化

### 1. 使用更快的模型
```python
# 简单提取任务使用更快的模型
llm = ChatOpenAI(model="gpt-3.5-turbo")
```

### 2. 批量处理
```python
# 一次性处理多个文本
batch_results = chain.batch([{"text": t} for t in texts])
```

### 3. 缓存结果
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def extract_info(text: str):
    return chain.invoke({"text": text})
```

## 对比其他方案

### vs 正则表达式
- **结构化输出**：更灵活，理解语义
- **正则表达式**：更快，但需要精确模式

### vs 传统 NLP
- **结构化输出**：无需训练，开箱即用
- **传统 NLP**：需要标注数据和训练

## 下一步

完成结构化输出学习后，可以继续探索：
- 09-多智能体协作
- 10-流式输出 + ChatUI
- 11-生产级追踪
- 11-生产级追踪

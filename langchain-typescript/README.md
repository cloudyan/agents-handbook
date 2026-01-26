# TypeScript 示例

使用 pnpm + tsx 管理环境和运行的 LangChain TypeScript 示例集合。

## 快速开始

### 1. 安装 pnpm

```bash
npm install -g pnpm
```

### 2. 安装依赖

```bash
cd langchain-typescript
pnpm install
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥
```

### 4. 验证环境

```bash
pnpm check-env
```

### 5. 运行示例

```bash
# 基础链
pnpm 01-hello-chain

# 提示词模板
pnpm 02-prompt-template

# 带记忆的对话
pnpm 03-memory-chat

# 检索增强问答
pnpm 04-rag-qa

# 天气智能体
pnpm 05-agent-weather

# API 服务
pnpm 06-api-deployment
```

## 可用命令

```bash
# 开发模式（监听文件变化）
pnpm dev

# 构建项目
pnpm build

# 类型检查
pnpm check

# 代码检查
pnpm lint

# 代码格式化
pnpm format
```

## 目录结构

```
langchain-typescript/
├── src/
│   ├── 01-hello-chain.ts       # 基础链
│   ├── 02-prompt-template.ts   # 提示词模板
│   ├── 03-memory-chat.ts       # 带记忆的对话
│   ├── 04-rag-qa.ts            # 检索增强问答
│   ├── 05-agent-weather.ts     # 天气智能体
│   ├── 06-api-deployment.ts    # API 部署
│   └── check-env.ts            # 环境验证
├── package.json                # 项目配置
├── tsconfig.json               # TypeScript 配置
└── .env.example                # 环境变量模板
```

## 技术栈

- **运行时**: Node.js ≥ 18
- **包管理器**: pnpm
- **执行器**: tsx
- **框架**: LangChain TypeScript
- **类型检查**: TypeScript
- **代码风格**: ESLint + Prettier

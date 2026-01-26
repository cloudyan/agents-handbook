# AGENTS.md

This file provides guidance to neovate when working with code in this repository.

## WHY: Purpose and Goals
多框架 AI Agent 开发实战手册，涵盖 LangChain Python & TypeScript，通过 11 个渐进式示例帮助开发者掌握大模型应用开发，从基础链到生产级智能体。

## WHAT: Technical Stack
- **Python**: uv (包管理), Jupyter Lab (交互开发), LangChain (框架), FastAPI (部署)
- **TypeScript**: pnpm (包管理), tsx (运行时), LangChain (框架), Express (部署)
- **核心依赖**: OpenAI SDK, Chroma/FAISS (向量库), pytest/pytest (测试)
- **代码质量**: black/ruff (Python), eslint/prettier (TypeScript)

## HOW: Core Development Workflow
```bash
# Python - LangChain
cd langchain-python
uv sync && source .venv/bin/activate
jupyter lab 01-hello-chain/

# TypeScript - LangChain
cd langchain-typescript
pnpm install && pnpm 01-hello-chain

# 代码质量
cd langchain-python && uv run black . && uv run ruff check .
cd langchain-typescript && pnpm lint && pnpm format
```

## Progressive Disclosure

For detailed information, consult these documents as needed:

- `docs/agent/development_commands.md` - All build, test, lint, release commands
- `docs/agent/architecture.md` - Module structure and architectural patterns
- `docs/agent/testing.md` - Test setup, frameworks, and conventions

**When working on a task, first determine which documentation is relevant, then read only those files.**

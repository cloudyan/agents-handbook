# 运行方式测试文档

## 1. CLI 运行方式测试

```bash
cd langchain-python
uv run python 09-multi-agent/index.py
```

**预期结果：**
- 看到多智能体系统初始化信息
- 看到 Researcher、Coder、Reviewer Agent 注册成功
- 看到任务执行过程中的各 Agent 输出
- 最终看到汇总结果

## 2. LangGraph Web UI 运行方式测试

```bash
cd langchain-python
uv run langgraph dev --config langgraph.json
```

**预期结果：**
- 服务启动在 http://localhost:8123
- 浏览器自动打开（或手动访问）
- 看到 LangGraph Studio 界面
- 可以在界面中输入任务并查看执行流程

**测试步骤：**
1. 启动服务后，浏览器访问 http://localhost:8123
2. 在界面中找到 "多智能体协作系统" 图
3. 点击进入图的界面
4. 在输入框中输入任务，例如："实现一个快速排序算法"
5. 点击运行，观察执行流程
6. 查看各节点的输出和状态变化

## 3. 功能对比测试

在两种运行方式中测试相同任务：

### 测试任务 1：代码开发
```
实现一个快速排序算法，使用 Python 实现
```

### 测试任务 2：研究任务
```
研究 Python 的最佳实践
```

### 预期行为
1. **CLI 方式**：在终端看到详细的文本输出
2. **Web UI 方式**：在浏览器界面看到可视化的执行流程

## 4. 验证要点

### CLI 方式
- [ ] Supervisor 正确分析任务类型
- [ ] Researcher 正确生成研究报告
- [ ] Coder 正确编写代码
- [ ] Reviewer 正确审查代码
- [ ] 最终结果汇总正确

### Web UI 方式
- [ ] 服务正常启动
- [ ] 图形界面正常显示
- [ ] 可以输入任务
- [ ] 可以看到节点执行状态
- [ ] 可以查看各节点的输出

## 5. 故障排查

### CLI 运行失败
```bash
# 检查环境变量
cat .env

# 检查依赖
uv pip list | grep langgraph

# 重新同步依赖
uv sync
```

### Web UI 启动失败
```bash
# 检查端口占用
lsof -i :8123

# 检查配置文件
cat 09-multi-agent/langgraph.json

# 检查 graph.py 语法
uv run python -c "from 09-multi-agent.graph import app; print('OK')"
```

## 6. 性能对比

| 运行方式 | 启动时间 | 首次响应 | 调试便利性 |
|---------|---------|---------|-----------|
| CLI | 快 | 快 | 中等（文本输出） |
| Web UI | 慢 | 中等 | 高（可视化） |

## 7. 使用建议

- **开发阶段**：推荐 Web UI，便于调试和查看执行流程
- **生产环境**：推荐 CLI，性能更好，资源占用更少
- **演示教学**：推荐 Web UI，可视化效果更好
- **自动化测试**：推荐 CLI，便于集成到 CI/CD 流程

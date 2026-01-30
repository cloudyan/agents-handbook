# Mini Claude Code

模型是决策者。代码只是提供工具并运行循环。

传统助手：

```
用户 -> 模型 -> 文本回复
```

Agent 系统：

```bash
用户 -> 模型 -> [工具 -> 结果]* -> 回复
                ^_________|
```
星号很重要。模型**反复**调用工具，直到它决定任务完成。这将聊天机器人转变为自主代理。

核心逻辑 agentLoop：

```js
while (true) {
  const response = await model.invoke({messages, tools});
  const results = executeTools(response.tool_calls);
  messages.push(results);
}
```

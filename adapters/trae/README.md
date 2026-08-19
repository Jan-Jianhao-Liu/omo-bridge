# omo-bridge / adapters / trae — Trae Work adapter

把 omo-bridge 的纪律 Agent + ultrawork 挂到 **Trae Work**（字节 AI IDE）原生能力上。

## Trae 的扩展模型

Trae（字节 AI IDE）的扩展机制是：
- **rules**（cursorrules 风格，`.trae/rules/*.md`）—— 注入对话上下文的行为规则
- **MCP server** —— 外接工具
- **内置编辑器能力** —— 文件编辑、终端、搜索

**没有** OpenCode 式生命周期 hooks，也没有 DSH 的 `tool-subagent` spawn 机制。因此 Trae 版 ultrawork 是三个平台里「降级最多」的。

## 文件

| 文件 | 作用 |
|------|------|
| `rules/omo-bridge.md` | cursorrules 风格规则（Sisyphus 行为 + ultrawork 协议 + category 路由） |

## 安装

```bash
# 把 rules 文件放到 Trae 项目的规则目录
cp adapters/trae/rules/omo-bridge.md  <your-project>/.trae/rules/omo-bridge.md
# 或按 Trae 版本的 rules 路径调整（不同版本路径可能不同：.trae/rules 或 .cursor/rules）
```

放好后，Trae 会把该规则注入对话上下文，用户输入 `ultrawork <任务>` 即触发 Sisyphus 行为。

## 诚实声明：与 DSH / WorkBuddy 版的差异

| 维度 | DSH 版 | WorkBuddy 版 | Trae 版 |
|------|--------|--------------|---------|
| ultrawork 续跑 | `tool-todo` + continuable | `TaskCreate` + 多轮 prompt | 待办清单（手动 / 文件） |
| 多 agent 委派 | `tool-subagent`(spawn) 原生 | `Agent` 工具原生 | ❌ 无 spawn，靠分轮扮演 / MCP |
| 模型路由 | category → ollama model 精确 | category → subagent_type | category → prompt 能力档 |
| PoC 状态 | ✅ 5/5 阶段 PASS | 🔨 骨架 | 🔨 骨架 |

## 路线图（Trae adapter）

- [x] rules 骨架 + category 路由
- [ ] MCP server 方案（让 Trae 通过 MCP 调 omo-bridge 编排，补上 subagent 能力）
- [ ] 端到端 PoC（在 Trae 跑 ultrawork 任务）
- [ ] 待办清单持久化载体（文件 / Trae 任务系统）

# omo-bridge DSH 端到端 PoC 结果（真实 runtime 验证）

> 在真实 DSH runtime 上验证 omo-bridge DSH adapter 的工具执行层（不只是大脑层）。
> 验证方式：`dsh --profile headless`（非交互，答一任务打印结果退出）。

## 验证配置

| 项 | 值 |
|----|----|
| 命令 | `NODE_OPTIONS= dsh --profile headless "$(cat dsh-poc-prompt.txt)"` |
| 工作目录 | `examples/dsh-poc-workspace/`（空目录） |
| 模型 | `qwen3.5:4b`（provider `ollama-local`，think 默认开） |
| 时长 | 1m 24s，exit 0 |
| prompt | `examples/dsh-poc-prompt.txt`（Sisyphus 提示词 + 建 Node.js hello-world 任务） |
| session | `~/.dsh/sessions/.../session.jsonl.zstd`（解压见 `dsh-poc-session.jsonl`，81 行） |

## 执行轨迹（4 step，从 session jsonl 提取）

### Step 1 — Intent Gate ✅
模型推理：「用户需要 Node.js hello-world，我需要按 ultrawork 协议四个阶段执行，首先 Intent Gate 记录任务...」
- `todo_write`：写四阶段 todo（Intent Gate in_progress，其余 pending）

### Step 2 — Intent Gate 完成 → Codebase Assessment ✅
模型推理：「意图闸门阶段完成，进入第二阶段代码库评估」
- `todo_write`：Intent Gate→completed，Codebase Assessment→in_progress

### Step 3 — Codebase Assessment ✅
模型推理：「进行代码库评估，查看当前目录架构」
- `glob` pattern="*" path="." → 结果 `No files found`（目录空，正确）
- 证明 `tool-fs-search` 真实调用 + 返回真实结果

### Step 4 — Smart Delegation（中断）⚠️
模型推理：「当前目录空，适合创建 Node.js 项目。进入 Smart Delegation，创建 subagent 创建项目结构。使用 qwen3.5:4b（有工具能力）」
- **明确体现 category 路由意识**（知道 qwen3.5:4b 有 tool 能力、要用它当 subagent）
- 但 subagent spawn 在此中断，session 结束（step/end），未到 tool-fs 写文件

## 验证结论

### 通过项 ✅
1. dsh headless 真实启动 `qwen3.5:4b`（session 明确 `provider: ollama-local, model: qwen3.5:4b`）
2. ultrawork 四阶段协议真实触发（模型推理明说四阶段 + 逐步推进）
3. `tool-todo` 续跑机制生效（3 次 `todo_write`，状态 completed/in_progress 正确流转）
4. `tool-fs-search` 真实调用（`glob` + 真实结果 `No files found`）
5. category 路由意识（模型明说「qwen3.5:4b 有工具能力」，符合 adapter 的模型约束设计）

### 未通过 / 中断项 ⚠️
1. **subagent spawn 在 headless 模式中断**（Step 4）—— `tool-subagent`(spawn/continuable) 在非交互 headless 模式下未能完成子代理派生。属已知 v2 待校准项（`cordis.patch.yml` 的 persona/agentOptions schema 校准 + 可能需 `--profile` 带子代理能力）。
2. **workspace 无文件产物**——因 Step 4 中断，未到 `tool-fs` 写文件阶段。大脑层 + 单 agent 工具执行层已验证，多 agent 委派→产物链路待 v2 闭环。

## 诚实总结

本次端到端 PoC 比 `poc-dsh-sisyphus.py`（ollama 直测大脑层，5/5 PASS 但无真实工具执行）更进一步：

- **大脑层 + 单 agent 工具执行层**：完全可行 ✅（真 DSH runtime + 真 tool-todo + 真 tool-fs-search + ultrawork 协议四阶段触发）
- **多 agent 委派层**：待 v2（subagent spawn 在 headless 中断，需 cordis.patch schema 校准 + 可能换交互式 web profile 验证 spawn）

**不藏拙**：DSH adapter 当前 PoC 验证到「单 agent ultrawork」级别（Sisyphus 自己用 todo+glob 走四阶段），「多 agent 委派（spawn Hephaestus 子代理）」尚未在 headless 闭环。这与 `docs/architecture.md` 的降级映射表一致——多 agent subagent 实例化是 v2 路线图项。

## 复现

```bash
export NODE_OPTIONS=
DSH=/c/Users/Administrator/.workbuddy/binaries/node/versions/22.22.2/dsh
cd examples/dsh-poc-workspace   # 空工作目录
"$DSH" --profile headless "$(cat ../dsh-poc-prompt.txt)"
# 查看执行轨迹：
#   ~/.dsh/sessions/--<cwd>--/session-*/session.jsonl.zstd
#   （用 zstandard stream_reader 解压，见本目录 dsh-poc-session.jsonl）
```

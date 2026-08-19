# omo-bridge / adapters / dsh — DeepSeek Harness adapter

把 omo-bridge 的「纪律 Agent + 多模型路由 + ultrawork」理念挂到 **DeepSeek Harness (DSH)** 上。复用 DSH 原生 `tool-subagent` / `tool-todo` / `tool-goal` / `tool-str-replace-editor` / cordis patch 机制，**不重造**编排引擎。

## 为什么 DSH 能接近原生复刻 OMO

DSH（`@deepseek-ai/deepseek-harness`，开源）已内置：
- `dsh-tool-subagent`(spawn/continuable) + `tool-subagent-fork`(fork/one-shot) + `tool-subagent-control` — 多 agent 委派 + 后台续跑
- `dsh-tool-todo`(allowParallelInProgress) — todo 持久化（ultrawork 续跑命脉）
- `dsh-tool-goal` — 目标持久化
- `dsh-tool-ralph` — Ralph Loop（OMO 同源概念）
- `dsh-persona` / `dsh-agent-instructions` — agent 角色提示词注入
- `dsh-plan-mode` / `dsh-workflow` — 规划与工作流

omo-bridge 只需把这些原生能力**按 OMO 的 11 角色语义 + 5 类别路由组织起来**。

## 文件

| 文件 | 作用 |
|------|------|
| `ultrawork-trigger.md` | **PoC 入口**。粘贴进 DSH 会话即触发 Sisyphus + ultrawork 协议 |
| `category-model-map.yaml` | category → 本机 ollama 模型映射（含诚实约束） |
| `cordis.patch.yml` | 可选 cordis patch（自动注入提示词 + subagent 实例，schema 待 PoC 校准） |

## PoC 快速开始

前置：本地 ollama 已拉 `qwen3.5:4b` / `qwen3.5:2b` / `deepseek-r1:7b`；DSH 已装（`DSH_HOME=~/.dsh`）；`~/.dsh/cordis.patch.yml` 已启用 `tool-fs` / `tool-fs-search` / `tool-str-replace-editor` / `tool-todo` / `tool-goal` / `tool-subagent` 等核心工具（见主仓 `cordis.patch.yml` 参考）。

```bash
# 1. 启动 DSH（headless 或 web）
dsh                    # 或 dsh-web

# 2. 在 DSH 会话里，整段粘贴 adapters/dsh/ultrawork-trigger.md 的内容（--- 之间）

# 3. 粘贴后直接说任务，例如：
#    ultrawork 在 ./demo 建一个 Node.js hello-world 项目，写测试，跑通自检
```

Sisyphus 会按 ultrawork 四阶段执行：意图门 → 摸架构 → 按 category 委派子 agent（`tool-subagent`）→ 独立复验，用 `tool-todo` 续跑，不完成不停止。

## 诚实声明：OMO 特性在 DSH 的降级

| OMO 原生特性 | DSH 状态 | 说明 |
|--------------|----------|------|
| 54+ 生命周期 hooks | ❌ 无 | ultrawork 降级为「提示词驱动 + tool-todo 续跑」，非 hook 自动触发 |
| 11 纪律 Agent | 🔨 部分 | PoC 跑通 Sisyphus(主) + Hephaestus(deep) + Oracle(只读)；其余待 persona schema 校准后补 |
| Hashline（内容哈希验证编辑） | 🔨 降级 | 用 `tool-str-replace-editor` 前后读校验替代 |
| Team Mode（tmux 多 agent 可视化） | ❌ 无 | DSH 无 tmux 集成；多 agent 靠 `tool-subagent` 后台 |
| ultrawork 不完成不停止 | ✅ 等价 | 靠 Sisyphus 提示词 + `tool-todo` 续跑 + `backgroundMode: continuable` |

## 模型约束（重要）

本机 ollama 的 `deepseek-r1:7b` / `deepseek-coder-v2` **无 `tools` 能力标签**，`tool-subagent` 当 agent 调用会 400。因此：
- 需工具调用的 agent（Sisyphus / Hephaestus / Explore / Atlas）→ 只能绑 `qwen3.5:4b` / `qwen3.5:2b`
- 只读分析型 agent（Oracle / Metis / Momus）→ 可绑 `deepseek-r1:7b` 做推理顾问，**必须 `toolFilter.deny` 所有写工具**

详见 `category-model-map.yaml`。

## 路线图（DSH adapter）

- [x] ultrawork 触发提示词（PoC 入口）
- [x] category → model 映射
- [ ] cordis.patch.yml schema 校准（agent-instructions / persona 字段）
- [ ] 11 角色完整 subagent 实例
- [ ] 独立 profile `omo`（与 headless 并列）

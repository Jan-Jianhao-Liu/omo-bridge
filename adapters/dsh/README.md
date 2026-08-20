# omo-deepseek-harness / adapters / dsh — DeepSeek Harness adapter

把 [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（OMO）的「纪律 Agent + 多模型路由 + ultrawork」理念挂到 **DeepSeek Harness (DSH)** 上。复用 DSH 原生 `tool-subagent` / `tool-todo` / `tool-goal` / `tool-str-replace-editor` / cordis patch 机制，**不重造**编排引擎。

> 本项目不使用 OMO 的任何源代码，仅借鉴其架构理念（CC0-1.0 公有领域）。OMO 原生不支持 DeepSeek Harness 作为宿主，故本项目独立实现。

## 为什么 DSH 能接近原生复刻 OMO

DSH（`@deepseek-ai/deepseek-harness`，开源）已内置：
- `dsh-tool-subagent`(spawn/continuable) + `tool-subagent-fork`(fork/one-shot) + `tool-subagent-control` — 多 agent 委派 + 后台续跑
- `dsh-tool-todo`(allowParallelInProgress) — todo 持久化（ultrawork 续跑命脉）
- `dsh-tool-goal` — 目标持久化
- `dsh-tool-ralph` — Ralph Loop（OMO 同源概念）
- `dsh-persona` / `dsh-agent-instructions` — agent 角色提示词注入（AGENTS.md 发现机制）
- `dsh-plan-mode` / `dsh-workflow` — 规划与工作流

omo-deepseek-harness 只需把这些原生能力**按 OMO 的 11 角色语义 + 5 类别路由组织起来**。

## 文件

| 文件 | 作用 |
|------|------|
| `ultrawork-trigger.md` | **免安装入口**。粘贴进 DSH 会话即触发 Sisyphus + ultrawork 协议 |
| `AGENTS.md` | Sisyphus 提示词（自动注入版）。复制为 `~/.dsh/AGENTS.md` 后热加载生效 |
| `category-model-map.yaml` | category → 模型路由（deepseek-v4-flash） |
| `cordis.patch.yml` | 可选 cordis patch（预注册 OMO 角色 subagent 工具，schema 已校准，重启 dsh 生效） |

## 快速开始

前置：DSH 已装（`DSH_HOME=~/.dsh`）；默认 agent 模型为 `deepseek-v4-flash`（`~/.dsh/settings.yaml` 的 `agent-default-model`）；`~/.dsh/cordis.patch.yml` 已启用 `tool-fs` / `tool-fs-search` / `tool-str-replace-editor` / `tool-todo` / `tool-goal` / `tool-subagent` 等核心工具。

### 方式一：交互式（粘贴触发）

```bash
dsh   # 或 dsh-web

# 在 DSH 会话里，整段粘贴 adapters/dsh/ultrawork-trigger.md 的内容（--- 之间）
# 然后说任务，例如：
#   ultrawork 在 ./demo 建一个 Node.js hello-world 项目，写测试，跑通自检
```

### 方式二：Headless 非交互（自动化 / CI）

```bash
# ⚠️ 若 DSH 运行在注入了 safe-delete shim 的环境，先清 NODE_OPTIONS（否则 dsh 内 fs 失败）
export NODE_OPTIONS=
DSH=<dsh 可执行路径>   # which dsh 定位

# headless：答一个任务，打印 final assistant message，退出
"$DSH" --profile headless "你的任务（含 Sisyphus 提示词）"
```

### 方式三：自动注入（一次性配置，长期生效）

```bash
# 1) Sisyphus 提示词：复制为 DSH 用户全局指令文件（热加载，立即生效）
cp adapters/dsh/AGENTS.md ~/.dsh/AGENTS.md

# 2) OMO 角色 subagent 工具：把 adapters/dsh/cordis.patch.yml 里的
#    `- id: omo-subagent-*` 条目追加进 ~/.dsh/cordis.patch.yml
#    重启 dsh web 后生效：模型将多出 subagent_hephaestus / subagent_explore /
#    subagent_oracle 三个委派工具，设置 → 插件列表可见三个 active 条目。
```

## 诚实声明：OMO 特性在 DSH 的降级

| OMO 原生特性 | DSH 状态 | 说明 |
|--------------|----------|------|
| 54+ 生命周期 hooks | ❌ 无 | ultrawork 降级为「提示词驱动 + tool-todo 续跑」，非 hook 自动触发 |
| 11 纪律 Agent | 🔨 部分 | Sisyphus(主) 已跑通；Hephaestus / Explore / Oracle 子 agent 实例已按当前 dsh schema 校准（2026-08-20） |
| Hashline（内容哈希验证编辑） | 🔨 降级 | 用 `tool-str-replace-editor` 前后读校验替代 |
| Team Mode（tmux 多 agent 可视化） | ❌ 无 | DSH 无 tmux 集成；多 agent 靠 `tool-subagent` 后台 |
| ultrawork 不完成不停止 | ✅ 等价 | 靠 Sisyphus 提示词 + `tool-todo` 续跑 + `backgroundMode: continuable` |
| 命令执行（subprocess spawn pipe） | ⚠️ sandbox 限制 | DSH sandbox 拦 `child_process spawn(pipe)`（EPERM，文档化边界）；需 `sandbox_permissions` 升级或非 spawn 方式 |

## 模型

默认 agent 模型：**`deepseek-v4-flash`**（provider `deepseek-official`，支持 tools 调用）。类别路由见 `category-model-map.yaml`。

## 已知问题（诚实记录）

1. **模型 tool call 退化是概率性的**：qwen 系本地模型在 ~9k+ tokens 上下文有退化概率（长 prompt / 多轮后把 tool call 写成文本）。deepseek-v4-flash 云端模型在长上下文实测未见此问题。任务仍建议精简 prompt、控制上下文增长。
2. **subagent 角色实例仅在「重启后」挂载**：`cordis.patch.yml` 是启动时装载的，新增的 `omo-subagent-*` 工具行需要重启 dsh web 才出现在模型工具列表；`AGENTS.md` 则热加载即时生效。
3. **其余角色未实例化**：prometheus / atlas / metis / momus / librarian / multimodal-looker / sisyphus-junior 尚未按 `core/agents.yaml` 批量补齐（模式已打通，按需追加即可）。

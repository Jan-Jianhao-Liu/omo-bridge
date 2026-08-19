# omo-deepseek-harness 架构与设计决策

> 本文记录 omo-deepseek-harness 的设计取舍：为什么 OMO 原生不支持 DeepSeek Harness、为什么选「借鉴理念 + 独立实现」、核心层如何组织、OMO 特性在 DSH 上的降级映射、以及三轮真实 runtime PoC 的结论。

## 1. 设计目标与约束

**目标**：把 [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（OMO）的「纪律型 Agent + 多模型路由 + ultrawork」理念，做成一层跑在 **DeepSeek Harness (DSH)** 上的轻量适配。

**硬约束**：
- OMO 是 OpenCode 的 TS 插件，核心价值强依赖 OpenCode 54+ 生命周期 hooks + 工具调用通道 + session/todo 持久化。
- **OMO 原生不支持 DeepSeek Harness 作为宿主**——OMO 的插件模型绑定 OpenCode 的 plugin API，DSH 没有等价物。
- OMO 用 SUL 许可证（非 OSI 标准开源），fork 必须保留 SUL + 签 CLA。

## 2. 路线选择

| 路线 | 形态 | 选否 |
|------|------|------|
| A | fork OMO 源码 + 写 DSH adapter shim | ✗ 受 SUL+CLA 约束，且 hooks 无法映射 |
| **B** | **借鉴 OMO 理念，用 DSH 原生机制做轻量适配，共享 core 配置** | **✓** |
| C | 从零造跨平台编排 npm 包 | ✗ 工作量最大，非本仓库目标 |

选 B 的理由：OMO 的价值在「理念」（纪律 agent + 类别路由 + ultrawork 协议），不在「代码」。把理念抽成平台无关的 `core/`，DSH 写薄 adapter，用最小工作量落地，且不受 SUL 约束（不使用 OMO 源码，MIT）。

## 3. DSH 扩展模型（为什么能接近原生复刻 OMO）

DSH（`@deepseek-ai/deepseek-harness`，开源）已内置 OMO 编排所需的对应物：

| OMO 概念 | DSH 原生等价 |
|----------|-------------|
| `tool-todo`（todo 持久） | `dsh-tool-todo`（allowParallelInProgress） |
| `tool-subagent`(spawn) | `dsh-tool-subagent`（spawn/continuable）+ fork + control |
| `tool-goal`（目标持久） | `dsh-tool-goal` |
| Ralph Loop | `dsh-tool-ralph` |
| `persona`（agent 角色） | `dsh-persona` / `dsh-agent-instructions` |
| 规划 / 工作流 | `dsh-plan-mode` / `dsh-workflow` |
| 命令执行 | `tool-pwsh` / `tool-bash`（注意 sandbox spawn 限制，见 §6） |

omo-deepseek-harness 只需把这些原生能力按 OMO 的 11 角色语义 + 5 类别路由组织起来，**不重造**编排引擎。

## 4. core 共享层设计

平台无关的「大脑」：

- `agents.yaml` — 11 纪律 Agent 精简定义（role / default_category / needs_tools / desc）。沿用 OMO 角色命名以致敬，但不抄源码。
- `categories.yaml` — 5 任务类别（orchestrator/deep/quick/ultrabrain/visual）→ 模型能力要求。平台无关，具体 model 由 adapter 映射。
- `prompts/*.md` — 各 agent 系统提示词，用 `{{platform_tools}}` / `{{todo_backend}}` 占位，由 adapter 注入。
- `ultrawork.md` — 编排协议：四阶段（Intent Gate → Codebase Assessment → Smart Delegation → Independent Verification）+ todo 续跑 + 不完成不停止契约 + adapter 落地契约。

## 5. category → 模型路由

- `core/categories.yaml`：类别 → 模型能力要求（tool_calling / reasoning / long_context / speed / multimodal）。
- `adapters/dsh/category-model-map.yaml`：category → 具体模型路由。当前单模型池 **`deepseek-v4-flash`**（provider `deepseek-official`），类别差异通过 `reasoning_effort`（quick=medium / 其余=high）与 `needs_tools`（只读 agent 不暴露写工具）体现。
- 未来接入多模型池时，只改 adapter 的 routing，core 层不动。

## 6. OMO 原生特性 → DSH 降级映射（核心）

| OMO 原生特性 | DSH 状态 | 说明 |
|--------------|----------|------|
| 54+ 生命周期 hooks | ❌ 无 | ultrawork 降级为「提示词驱动 + tool-todo 续跑」，非 hook 自动触发 |
| 11 纪律 Agent | 🔨 部分 | PoC 跑通 Sisyphus(主)；subagent 多 agent 实例化待 cordis.patch persona schema 校准 |
| category 模型路由 | ✅ | category → deepseek-v4-flash + reasoning_effort |
| Hashline（哈希验证编辑） | 🔨 降级 | 用 `tool-str-replace-editor` 前后读校验替代 |
| ultrawork 不完成不停止 | ✅ 等价 | Sisyphus 提示词 + tool-todo 续跑 + backgroundMode continuable（v2 实证：模型 19 次重试不放弃） |
| Team Mode（tmux 多 agent 可视化） | ❌ 无 | DSH 无 tmux；多 agent 靠 tool-subagent 后台 |
| 命令执行 | ⚠️ sandbox 限制 | DSH sandbox 拦 `child_process spawn(pipe)`（EPERM，文档化边界）；需 `sandbox_permissions` 升级或非 spawn 方式 |

「降级」≠ 不可用，而是诚实承认：没有原生 hook 的平台上，某些自动化退化为「多轮 prompt 驱动 + 外部续跑」的等价形态。

## 7. PoC 结论（真实 DSH runtime，headless 非交互）

| 轮 | 结果 |
|----|------|
| v1（长 prompt + subagent 委派） | 四阶段触发 + tool-todo + glob 真调用；Step4 模型 tool call 退化（长 prompt ~8.8k tokens） |
| v2（精简 prompt + 单 agent） | **39 step 无退化**；tool-fs 真建 3 文件；不完成不停止契约实证；命令执行被缺 PowerShell 7 阻塞 |
| v2.1（装 PowerShell 7.6.5） | **37 step 无退化**（23k+ tokens）；文件 + 运行 + 测试闭环；todo 4/4；agent 诚实报告 sandbox 限制 |

**验证结论**：大脑层（ultrawork 协议）✅ / tool 层（todo/fs/subagent）✅ / 环境层（命令执行）✅ 全部可行。详见 `examples/dsh-poc-result.md` + `dsh-poc-v2-result.md`。

## 8. 许可证策略

- 本项目 **MIT**，版权 英壳科技武汉有限公司。
- **不使用 OMO 任何源码**，仅借鉴理念，从零实现。
- README 顶部 + LICENSE 均明确致敬声明 + 主仓链接，规避 SUL 约束。
- Agent 命名（Sisyphus 等）作为概念命名沿用，非代码引用。

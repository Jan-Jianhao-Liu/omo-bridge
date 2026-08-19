# omo-bridge 架构与设计决策

> 本文记录 omo-bridge 的设计取舍、三平台扩展模型对比、OMO 原生特性降级映射，以及为什么选「路线 B + DSH 优先 + MIT 自建」。

## 1. 设计目标与约束

**目标**：把 [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（OMO）的「纪律型 Agent + 多模型路由 + ultrawork」理念，做成一层跨平台轻量适配，首批打通 DSH，并预留 WorkBuddy / Trae Work。

**硬约束**：
- OMO 是 OpenCode 的 TS 插件，核心价值强依赖 OpenCode 54+ 生命周期 hooks + 工具调用通道 + session/todo 持久化。
- 三个目标平台的扩展模型不统一，没有「OpenCode plugin API」等价物。
- OMO 用 SUL 许可证（非 OSI 标准开源），fork 必须保留 SUL + 签 CLA 才能 PR 回主仓。

## 2. 路线选择

| 路线 | 形态 | 工作量 | license | 选否 |
|------|------|--------|---------|------|
| A | fork OMO 源码 + 写 3 个 adapter shim | 数周 | 受 SUL+CLA 约束 | ✗ |
| **B** | **借鉴理念，三平台各用原生机制做轻量版，共享 core 配置** | **1-2 周 PoC** | **MIT 自由** | **✓** |
| C | 从零造跨平台编排 npm 包 | 数月 | 自由 | ✗ |

选 B 的理由：OMO 的价值在「理念」（纪律 agent + 类别路由 + ultrawork 协议），不在「代码」。把理念抽成平台无关的 `core/`，各平台写薄 adapter，能用最小工作量覆盖三平台，且不受 SUL 约束。

## 3. 三平台扩展模型对比

| 维度 | DSH | WorkBuddy | Trae Work |
|------|-----|-----------|-----------|
| 扩展机制 | `settings.yaml` + cordis patch + profiles | Skill(SKILL.md) + MCP + Expert | rules(cursorrules) + MCP |
| hook 生命周期 | 半套（cordis 编排） | 无（prompt+tool 注入） | 无（上下文规则） |
| 独立 tool 通道 | 有（`@deepseek-ai/dsh-tool-*`） | 有（内置 + MCP） | 有（内置 + MCP） |
| 子代理 spawn | ✅ `tool-subagent`(spawn/continuable) | ✅ `Agent` 工具 | ❌ 无（靠 MCP / 分轮扮演） |
| todo 持久 | ✅ `tool-todo` | ✅ `TaskCreate/Update/List` | 待办（手动/文件） |
| 目标持久 | ✅ `tool-goal` | Skill 上下文 | rules 上下文 |
| 多 agent 原生度 | 高（已含 ralph/workflow/persona） | 中（Agent + Task） | 低（无 spawn） |

**关键洞察**：DSH 和 WorkBuddy 几乎一一对应（tool-todo↔TaskCreate, tool-subagent↔Agent），能接近原生复刻 OMO；Trae 最弱，需 MCP server 补 subagent 能力。

## 4. core 共享层设计

平台无关的「大脑」：

- `agents.yaml` — 11 纪律 Agent 精简定义（role / default_category / needs_tools / desc）。沿用 OMO 角色命名以致敬，但不抄源码。
- `categories.yaml` — 5 任务类别（orchestrator/deep/quick/ultrabrain/visual）→ 模型能力要求。平台无关，具体 model 由 adapter 映射。
- `prompts/*.md` — 各 agent 系统提示词，用 `{{platform_tools}}` / `{{todo_backend}}` 占位，由 adapter 注入。
- `ultrawork.md` — 编排协议：四阶段（Intent Gate → Codebase Assessment → Smart Delegation → Independent Verification）+ todo 续跑 + 不完成不停止契约 + adapter 落地契约。

## 5. OMO 原生特性 → 三平台降级映射（核心）

| OMO 原生特性 | DSH | WorkBuddy | Trae |
|--------------|-----|-----------|------|
| 54+ 生命周期 hooks | ❌ → prompt+tool-todo 续跑 | ❌ → prompt+TaskCreate 续跑 | ❌ → rules+待办 |
| 11 纪律 Agent | 🔨 部分（PoC Sisyphus/Hephaestus/Oracle） | 🔨（subagent_type 映射） | 🔨（rules 角色段） |
| category 模型路由 | ✅ category→ollama model 精确 | ⚠️ category→subagent_type（能力档） | ⚠️ category→prompt 能力档 |
| Hashline（哈希验证编辑） | 🔨 → str-replace-editor 前后读校验 | 🔨 → Edit 前后读校验 | 🔨 → 编辑器 diff 校验 |
| ultrawork 不完成不停止 | ✅ 等价（prompt+todo+continuable） | ✅ 等价（prompt+Task 续跑） | 🔨 靠 rules+用户驱动 |
| Team Mode（tmux 多 agent 可视化） | ❌ 无 tmux | ❌ | ❌ |
| Background Agents（5+ 并行） | ✅ tool-subagent continuable | ✅ Agent background | ❌ |
| Skills 系统（携 MCP） | ✅ MCP 原生 | ✅ Skill+MCP | ✅ MCP |
| /init-deep（层级 AGENTS.md） | 可做（agent-instructions） | 可做（Skill 知识库） | 可做（rules 层级） |

「降级」≠ 不可用，而是诚实承认：在没有原生 hook 的平台上，某些自动化退化为「多轮 prompt 驱动 + 外部续跑」的等价形态。

## 6. DSH adapter 设计与 PoC

**设计**：复用 DSH 原生 `tool-subagent`(persona+agentOptions.model+toolFilter+continuable) + `tool-todo` + `tool-goal` + cordis patch，把 OMO 11 角色挂成 subagent 实例 + Sisyphus 提示词注入。

**PoC**（`examples/poc-dsh-sisyphus.py`）：因无法在 WorkBuddy 内驱动 DSH 交互会话，改用 ollama `/api/chat`(think:false) 直接测「Sisyphus 提示词 + qwen3.5:4b」能否进入 ultrawork 行为模式。

**结果**：5/5 阶段 PASS ✅
- Intent Gate ✅ / Codebase Assessment ✅ / Smart Delegation ✅ / Independent Verification ✅ / ultrawork 契约 ✅
- 模型自然产出 DSH 工具调用 JSON（`tool-fs` / `tool-pwsh` / `tool-todo`），且明说「不相信子代理自述，直接跑 npm test」。
- 证明 adapter 大脑层完全可行；DSH 工具执行层留给用户在本地 DSH 真跑（见 `adapters/dsh/README.md` PoC 步骤）。

**模型约束**（以用户实测为准）：ollama 上 `deepseek-r1:7b` / `deepseek-coder-v2` 无 `tools` 能力标签，需 tool 的 agent 只能绑 `qwen3.5:4b`/`2b`；只读 agent（Oracle/Metis/Momus）可绑 deepseek 系做推理顾问，必须 `toolFilter.deny` 写工具。

## 7. WorkBuddy / Trae adapter 设计

**WorkBuddy**：映射表显示原生 TaskCreate/Agent/Edit 与 DSH 一一对应，适配性极好。SKILL.md 作触发入口，category→`subagent_type` 路由。未端到端测（骨架）。

**Trae**：最弱平台，无 spawn。rules 注入行为，subagent 能力待 MCP server 方案补（路线图）。

## 8. 许可证策略

- 本项目 **MIT**，版权 英壳科技武汉有限公司。
- **不使用 OMO 任何源码**，仅借鉴理念，从零实现。
- README 顶部 + LICENSE 均明确致敬声明 + 主仓链接，规避 SUL 约束。
- Agent 命名（Sisyphus 等）作为概念命名沿用，非代码引用。

## 9. 路线图

- [x] core 共享层（agents/categories/ultrawork/prompts）
- [x] DSH adapter + PoC 5/5 PASS
- [x] WorkBuddy adapter 骨架
- [x] Trae adapter 骨架
- [ ] DSH cordis.patch.yml schema 校准（agent-instructions / persona 字段）
- [ ] DSH 11 角色完整 subagent 实例
- [ ] WorkBuddy 端到端 PoC + Skill 安装机制
- [ ] Trae MCP server 方案（补 subagent）
- [ ] 三平台一致性测试套件
- [ ] category→model 路由的可配置化

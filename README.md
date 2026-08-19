# omo-bridge

> 借鉴 [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（OMO）的「纪律型 Agent + 多模型路由 + ultrawork」理念，做成一层跨平台轻量适配，首批打通 **DeepSeek Harness (DSH)**，并预留 **WorkBuddy** 与 **Trae Work** 的接入位。

## 致敬声明

本项目受 [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（作者 [code-yeongyu](https://github.com/code-yeongyu)，许可证 **SUL**）的架构理念启发。

- **本项目不使用 OMO 的任何源代码**，仅借鉴其「纪律 Agent / 类别路由 / ultrawork 协议」的设计思想，从零实现。
- 因此本项目的许可证为 **MIT**，不受 SUL 约束；Agent 命名（Sisyphus / Hephaestus / Prometheus ...）作为概念命名沿用，以表达理念来源。
- 若你想要 OMO 的完整能力（11 agent + 54 hooks + Hashline + Team Mode），请直接用原版：`bunx oh-my-openagent install`（需 OpenCode 宿主）。

## 为什么不直接用 OMO

OMO 的核心价值强依赖底层 harness 提供三样东西：

1. **54+ 生命周期 hooks**（`chat.params` / `tool.pre/post` / `session.idle`）
2. **工具调用通道**（edit / bash / read / grep）
3. **session + todo 持久化**

而 DSH / WorkBuddy / Trae Work 三个目标平台的扩展模型**不统一**，没有「OpenCode plugin API」的等价物：

| 平台 | 扩展机制 | hook 生命周期 | 独立 tool 通道 |
|------|----------|--------------|----------------|
| DSH | `settings.yaml` provider 路由 + cordis 编排 + agent presets | 半套（cordis 有编排） | 有（cordis agent 可调 tool） |
| WorkBuddy | Skill(SKILL.md) + MCP connector + Expert | 无（prompt+tool 注入） | 有（MCP / 内置工具） |
| Trae Work | MCP + rules（cursorrules 风格） | 无（上下文规则） | 有（MCP） |

结论：把 OMO 原样「提取」到这三个平台 ≈ 重写。omo-bridge 选择**只搬理念、不搬代码**——把 OMO 的「大脑」（agent 定义 + 类别路由 + ultrawork 协议）抽成平台无关的 `core/`，再给每个平台写一层薄薄的 adapter。

## 架构

```
omo-bridge/
├── core/                  # 平台无关的「大脑」
│   ├── agents.yaml        # 11 纪律 Agent 精简定义 (role / category / needs_tools / desc)
│   ├── categories.yaml    # 任务类别 → 模型能力要求 (具体模型由 adapter 映射)
│   ├── prompts/           # 各 agent 的系统提示词
│   └── ultrawork.md       # ultrawork 编排协议 (多轮驱动 + todo 持久 + 不完成不停止 + 独立验证)
├── adapters/              # 三平台薄接入层
│   ├── dsh/               # ★ 首批完整实现：cordis preset + provider 路由 + agent presets
│   ├── workbuddy/         # 骨架 + TODO：Skill(SKILL.md) + 可选 MCP
│   └── trae/              # 骨架 + TODO：rules + MCP server
├── docs/
│   └── architecture.md    # 设计决策 + OMO 特性降级映射表
├── examples/
└── README.md
```

## 三平台适配进度

| 平台 | 状态 | ultrawork | Hashline | 多模型路由 | 备注 |
|------|------|-----------|----------|-----------|------|
| DSH | ✅ PoC | 降级(多轮 prompt+todo) | 降级(读写校验) | ✅ provider 路由 | ollama 本地模型池 |
| WorkBuddy | 🔨 骨架 | 降级(TaskCreate 续跑) | — | 待定 | Skill 体系 |
| Trae Work | 🔨 骨架 | 降级(rules 驱动) | — | 待定 | MCP + rules |

「降级」≠ 不可用，而是诚实承认：在没有 OpenCode 式 hook 的平台上，OMO 的某些自动化会退化成「多轮 prompt 驱动 + 外部 todo 续跑」的等价形态，而非原生生命周期触发。

## DSH 快速开始（首批完整 adapter）

前置：本地已装 ollama + DSH（`ollama launch dsh` 或等价方式），`DSH_HOME=C:\Users\Administrator\.dsh`。

```bash
# 1. 把 adapter 的 settings 片段合并进你的 ~/.dsh/settings.yaml
#    （见 adapters/dsh/settings.patch.yaml，含 provider 路由 + agent presets）

# 2. 把 ultrawork 协议与 agent 提示词放进 cordis profile
#    （见 adapters/dsh/profiles/ultrawork.yml）

# 3. 在 DSH 会话里输入 ultrawork 触发编排
```

详见 `adapters/dsh/README.md`。

## 本机模型池约束（DSH adapter 诚实标注）

DSH adapter 的模型映射受本机 ollama 能力限制：

| 类别 | 命中模型 | 可否当 agent（需 tool calling） |
|------|----------|--------------------------------|
| orchestrator / deep | `qwen3.5:4b` | ✅ 可（主 agent） |
| quick | `qwen3.5:2b` | ✅ 可（快速 agent） |
| ultrabrain（推理） | `deepseek-r1:7b` / `deepseek-coder-v2` | ❌ 仅推理，不调 tool |
| visual | 暂缺（本机无多模态模型） | — |

> ollama 上的 `deepseek-r1:7b` / `deepseek-coder-v2` **无 `tools` 能力标签**，DSH 调用会报 400。因此需要工具调用的 agent（Sisyphus / Hephaestus / Atlas ...）只能绑 `qwen3.5:4b`；只读分析型 agent（Oracle / Metis / Momus）才可绑 deepseek 系做推理顾问。

## 路线图

- [x] 项目骨架 + core 共享层
- [x] DSH adapter 完整 + 端到端 PoC
- [ ] WorkBuddy adapter（Skill + MCP）
- [ ] Trae Work adapter（rules + MCP）
- [ ] 三平台一致性测试套件
- [ ] 类别路由的可配置化（让用户自定义 category → model 映射）

## License

MIT — 见 [LICENSE](./LICENSE)。

本项目不包含 oh-my-openagent 的源代码。oh-my-openagent 的所有权利归其原作者所有，采用 SUL 许可证。

<div align="center">

# omo-deepseek-harness

**把 oh-my-openagent（OMO）的纪律型 Agent 编排带到 DeepSeek Harness。**

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

</div>

## 这是什么？

`omo-deepseek-harness` 把 [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（OMO）的 **纪律型 Agent + 多模型路由 + ultrawork** 理念带到 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（DSH）——一个轻量、独立实现的适配层，**CC0-1.0** 公有领域协议。

输入一次 `ultrawork`。Sisyphus 开始编排：解析意图 → 摸清代码库 → 按类别委派 → 独立验证。不完成不停止。

## 特性

- **一词触发** — 输入 `ultrawork`（或 `ulw`），Sisyphus 接管并把任务推进到完成。
- **纪律 Agent 委派** — 预注册角色子代理（`subagent_hephaestus` / `subagent_explore` / `subagent_oracle`），基于 DSH 原生 `tool-subagent`。
- **ultrawork 四阶段协议** — 意图门 → 代码库评估 → 按类别智能委派 → 独立验证。
- **不完成不停止** — 通过 `tool-todo` / `tool-goal` 持久化续跑；中断后从断点继续。
- **不重造引擎** — 薄适配层复用于 DSH 原生能力，而非新编排运行时。

## 致敬声明

受 [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent)（作者 [code-yeongyu](https://github.com/code-yeongyu)，**SUL** 协议）启发。

- 本项目**不使用** OMO 的任何源代码，仅从零重实现其架构*理念*（纪律 Agent / 类别路由 / ultrawork 协议）。
- Agent 命名（Sisyphus / Hephaestus / Prometheus ...）作为概念致敬沿用。
- 需要 OMO 完整能力（11 agent + 54 hooks + Hashline + Team Mode）请用原版：`bunx oh-my-openagent install`（需 OpenCode 宿主）。

## 为什么不用 OMO？

**OMO 原生不支持 DeepSeek Harness。** OMO 是 OpenCode 插件，其核心价值依赖 OpenCode 的 54+ 生命周期 hooks、工具调用通道、session/todo 持久化——DSH 均无等价物。原样移植 OMO ≈ 重写，且受 SUL + CLA 约束。

本项目只把「大脑」（Agent 定义 + 类别路由 + ultrawork 协议）抽到平台无关的 `core/`，再加一层薄 adapter 映射到 DSH 原生能力（`tool-subagent` / `tool-todo` / `tool-goal` ...）——**不重造引擎**。

## 架构

```
omo-deepseek-harness/
├── core/                  # 平台无关的「大脑」
│   ├── agents.yaml        # 11 纪律 Agent（role / category / needs_tools / desc）
│   ├── categories.yaml    # 任务类别 → 模型能力要求
│   ├── prompts/           # agent 系统提示词（{{platform_tools}} 占位）
│   └── ultrawork.md       # ultrawork 协议：四阶段 + todo 续跑 + 不完成不停止
├── adapters/dsh/          # DeepSeek Harness 适配层（薄层）
│   ├── ultrawork-trigger.md      # 快速入口：粘贴进 DSH 会话即触发 Sisyphus
│   ├── AGENTS.md                 # Sisyphus 提示词：复制为 ~/.dsh/AGENTS.md（热加载生效）
│   ├── category-model-map.yaml   # category → deepseek-v4-flash 路由
│   └── cordis.patch.yml          # 可选：预注册 OMO 角色 subagent 工具（schema 已校准）
└── docs/architecture.md   # 设计决策 + OMO 特性降级映射
```

## 快速开始（DSH）

前置：已装 DSH（`DSH_HOME=~/.dsh`），默认 agent 模型 `deepseek-v4-flash`，`~/.dsh/cordis.patch.yml` 已启用核心工具（`tool-fs` / `tool-todo` / `tool-subagent` ...）。

### 交互式

```bash
dsh    # 或 dsh-web

# 把 adapters/dsh/ultrawork-trigger.md 的内容（--- 之间）粘贴进会话，然后说：
#   ultrawork 在 ./demo 建一个 Node.js hello-world 项目，写测试，跑通自检
```

### Headless（自动化 / CI）

```bash
"$DSH" --profile headless "你的任务"
```

## License

**CC0 1.0 Universal（公有领域）** — 见 [LICENSE](./LICENSE)。不声明任何版权人，不要求署名。

本项目不含 oh-my-openagent 的任何源代码。oh-my-openagent 的全部权利归原作者所有，SUL 协议。

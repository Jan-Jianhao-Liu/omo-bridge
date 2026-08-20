<p align="center">
  <img src="assets/waifu_banner.png" width="100%" alt="omo-deepseek-harness · 命运塔楼大法师圣女" />
</p>

命令我已下达——键入 `ultrawork`。在任务完成之前，这座塔楼的符环永不停止转动。

---

<div align="center">

# omo-deepseek-harness

**Bring the discipline-agent orchestration of oh-my-openagent (OMO) to DeepSeek Harness.**

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

</div>

## What is this?

`omo-deepseek-harness` brings the **discipline-agent + multi-model routing + ultrawork** philosophy of [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) (OMO) to [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (DSH) — a lightweight, independently-implemented adapter, released to the public domain under **CC0-1.0**.

Type `ultrawork` once. Sisyphus orchestrates: parse intent → assess the codebase → delegate by category → verify independently. It does not stop until done.

## Features

- **One-word trigger** — type `ultrawork` (or `ulw`) and Sisyphus drives the task to completion.
- **Discipline-agent delegation** — pre-registered role subagents (`subagent_hephaestus`, `subagent_explore`, `subagent_oracle`) on DSH's native `tool-subagent`.
- **4-phase ultrawork protocol** — intent gate → codebase assessment → smart delegation by category → independent verification.
- **Never-stop contract** — todo-persisted resumption via `tool-todo` / `tool-goal`; interrupted runs continue from the last checkpoint.
- **No engine re-invention** — a thin adapter over DSH's native tooling, not a new orchestration runtime.

## Attribution

Inspired by [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) by [code-yeongyu](https://github.com/code-yeongyu), licensed under **SUL**.

- This project uses **none** of OMO's source code. It re-implements the architectural *philosophy* (discipline agents / category routing / ultrawork protocol) from scratch.
- Agent names (Sisyphus, Hephaestus, Prometheus, ...) are used as conceptual homage.
- For OMO's full capabilities (11 agents + 54 hooks + Hashline + Team Mode), use the original: `bunx oh-my-openagent install` (requires OpenCode as host).

## Why not just use OMO?

**OMO does not natively support DeepSeek Harness.** OMO is an OpenCode plugin whose core value depends on OpenCode's 54+ lifecycle hooks, tool-calling channel, and session/todo persistence — none of which exist as-is in DSH. Porting OMO as-is would effectively be a rewrite, constrained by its SUL license + CLA.

This project takes only the *brain* (agent definitions + category routing + ultrawork protocol) into a platform-agnostic `core/`, plus a thin adapter that maps onto DSH's native capabilities (`tool-subagent`, `tool-todo`, `tool-goal`, ...) — **no engine re-invention**.

## Architecture

```
omo-deepseek-harness/
├── core/                  # Platform-agnostic "brain"
│   ├── agents.yaml        # 11 discipline agents (role / category / needs_tools / desc)
│   ├── categories.yaml    # task category → model capability requirements
│   ├── prompts/           # agent system prompts ({{platform_tools}} placeholders)
│   └── ultrawork.md       # ultrawork protocol: 4-phase + todo continuity + never-stop
├── adapters/dsh/          # DeepSeek Harness adapter (the thin layer)
│   ├── ultrawork-trigger.md      # quick entry: paste into a DSH session to trigger Sisyphus
│   ├── AGENTS.md                 # Sisyphus prompt: copy to ~/.dsh/AGENTS.md (hot-reloads)
│   ├── category-model-map.yaml   # category → deepseek-v4-flash routing
│   └── cordis.patch.yml          # optional: pre-registered OMO subagent tools (schema-calibrated)
└── docs/architecture.md   # design decisions + OMO-feature degradation map
```

## Quick Start (DSH)

Prereqs: DSH installed (`DSH_HOME=~/.dsh`), default agent model `deepseek-v4-flash`, core tools enabled in `~/.dsh/cordis.patch.yml` (`tool-fs`, `tool-todo`, `tool-subagent`, ...).

### Interactive

```bash
dsh    # or dsh-web

# Paste adapters/dsh/ultrawork-trigger.md (between the --- markers) into the session,
# then say:
#   ultrawork build a Node.js hello-world project in ./demo, write tests, run them
```

### Auto-inject (one-time setup, keeps working across sessions)

```bash
# 1) Sisyphus instructions: copy to DSH's user-global instructions file (hot-reloads)
cp adapters/dsh/AGENTS.md ~/.dsh/AGENTS.md

# 2) OMO role subagent tools: append the `- id: omo-subagent-*` entries from
#    adapters/dsh/cordis.patch.yml to ~/.dsh/cordis.patch.yml, then restart dsh web.
#    You get subagent_hephaestus / subagent_explore / subagent_oracle delegation tools.
```

### Headless (automation / CI)

```bash
"$DSH" --profile headless "your task"
```

## License

**CC0 1.0 Universal (public domain)** — see [LICENSE](./LICENSE). No copyright holder is asserted; no attribution required.

This project contains no source code from oh-my-openagent. All rights to oh-my-openagent belong to its author, under the SUL license.

<div align="center">

# omo-deepseek-harness

**Bring the discipline-agent orchestration of oh-my-openagent (OMO) to DeepSeek Harness.**

[English](README.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md)

</div>

## What is this?

`omo-deepseek-harness` brings the **discipline-agent + multi-model routing + ultrawork** philosophy of [oh-my-openagent](https://github.com/code-yeongyu/oh-my-openagent) (OMO) to [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) (DSH) — a lightweight, independently-implemented adapter, licensed under **MIT**.

Type `ultrawork` once. Sisyphus orchestrates: parse intent → assess the codebase → delegate by category → verify independently. It does not stop until done.

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
│   ├── ultrawork-trigger.md      # PoC entry: paste into a DSH session
│   ├── AGENTS.md                 # Sisyphus prompt: copy to ~/.dsh/AGENTS.md (hot-reloads)
│   ├── category-model-map.yaml   # category → deepseek-v4-flash routing
│   └── cordis.patch.yml          # optional: pre-registered OMO subagent tools (schema-calibrated)
├── examples/              # PoC scripts + evidence (analyze-dsh-session.py, poc results)
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
"$DSH" --profile headless "your task (see examples/dsh-poc-prompt.txt)"
```

## PoC Evidence (real DSH runtime)

Three headless end-to-end runs — full analysis in `examples/`:

| Round | Result |
|-------|--------|
| v1 (long prompt + subagent) | 4-phase triggered, `tool-todo` + `glob` real calls; Step4 model tool-call degeneration (long prompt) |
| v2 (concise prompt + single agent) | **39 steps, zero degeneration**; `tool-fs` created 3 files; never-stop contract proven (19 retries); command exec blocked by missing shell |
| v2.1 (fixed env) | **37 steps, zero degeneration** (23k+ tokens); files + run + test closed loop; todo 4/4; agent honestly reported sandbox limits |

Honest limitations are documented in `docs/architecture.md` — e.g. OMO's hook-based automation degrades to prompt-driven + todo-continuity on DSH, and DSH's sandbox blocks `child_process spawn(pipe)` (documented boundary, needs `sandbox_permissions` escalation).

## License

MIT — see [LICENSE](./LICENSE). Copyright 英壳科技武汉有限公司.

This project contains no source code from oh-my-openagent. All rights to oh-my-openagent belong to its author, under the SUL license.

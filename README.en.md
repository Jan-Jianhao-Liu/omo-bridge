<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/Jan-Jianhao-Liu/Jan-Jianhao-Liu.github.io/assets/waifu_omo_banner.jpg" width="100%" alt="omo-deepseek-harness · 命运塔楼大法师圣女" />
</p>

---

<div align="center">

# omo-deepseek-harness

**Bring the discipline-agent orchestration of oh-my-openagent (OMO) to DeepSeek Harness.**

[简体中文](README.md) · [English](README.en.md) · [日本語](README.ja.md)

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

## Benchmarks

Controlled experiment on **DeepSeek Harness**: the same software spec (a Markdown→HTML converter) built by control (no omo) vs omo (ultrawork 4-phase) agents. Success is judged by an **independent hidden acceptance suite + coverage + measured performance** run by the parent agent — not by what the sub-agent claims. Model: `deepseek-v4-flash`, 3 runs per group.

> Each group ran 3 independent repetitions (run1-run3); each bar corresponds to one run of that group.

### Core comparison (median)

| Dimension | control | omo | Δ |
|---|---|---|---|
| **Product · hidden acceptance (23)** | 23/23 ✅ | 23/23 ✅ | no diff |
| **Product · line coverage** | 97.3% | 95.4% | −1.9pp |
| **Product · 300KB perf** | 30.8ms | 33.0ms | ≈ |
| Product · implementation LOC | 237 | 284 | +20% |
| **Process · steps** | 17 | 9 | **−47%** |
| **Process · est. cost** | $0.060 | $0.050 | **−18%** |
| **Process · build time** | 191s | 316s | **+65%** |
| Process · total / reasoning tokens | 39.3k / 17.8k | 33.4k / 17.0k | ≈ |

### Charts

![steps](https://testingcf.jsdelivr.net/gh/Jan-Jianhao-Liu/Jan-Jianhao-Liu.github.io/assets/benchmark/en/steps.svg)
![build time](https://testingcf.jsdelivr.net/gh/Jan-Jianhao-Liu/Jan-Jianhao-Liu.github.io/assets/benchmark/en/buildtime.svg)
![cost](https://testingcf.jsdelivr.net/gh/Jan-Jianhao-Liu/Jan-Jianhao-Liu.github.io/assets/benchmark/en/cost.svg)

### Conclusion

- **Output quality is identical**: both groups ship spec-compliant software passing **23/23 (incl. 4 XSS-escaping checks)** — with a clear spec, omo does not change output correctness.
- **omo earns its keep in the process**: **steps −47%, est. cost −18%** (plan-first ⇒ far fewer fix-it-up rework micro-steps; fewer steps ⇒ less cache re-read). Cost: **+65% build time** (more planning/verification per step); tokens roughly even.
- **Complexity inflection**: on trivial tasks (v1) omo is pure overhead; on complex tasks (v2) it flips to an efficiency win — consistent with "value grows with task complexity".

### Recommendations

- **Complex, multi-step, rework-prone builds** → enable omo (plan-first + independent verification; measurably fewer rework steps, lower cost).
- **Trivial single-step tasks** → skip omo, plain DSH (v1 showed it is pure overhead).
- **Minimize wall-clock** → skip omo; **minimize cost + want stable quality & discipline** → enable omo.
- omo's enforced **4th-phase independent verification** is its core guard against cargo-cult/leaky work — keep it for complex edits.
- Limitation: n=3, one task, one model — directional not conclusive; re-run on a larger sample for significance. Full data & reproducibility in [`docs/benchmark`](docs/benchmark).

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
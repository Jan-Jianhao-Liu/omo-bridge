#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
omo-bridge / examples / poc-dsh-sisyphus.py

PoC: 验证 omo-bridge DSH adapter 的「大脑层」可行性。
不依赖 DSH runtime（无法在 WorkBuddy 内驱动 DSH 交互会话），而是用 ollama /api/chat
直接测：把 adapters/dsh/ultrawork-trigger.md 的 Sisyphus 系统提示词注入 qwen3.5:4b，
看模型是否能进入 ultrawork 四阶段行为模式 + category 委派 + 独立验证。

通过标准（关键词命中）：
  - Intent Gate      : 意图 / intent / 真实意图
  - Codebase Assess  : 架构 / 评估 / 摸 / explore / grep
  - Smart Delegation : 委派 / category / subagent / hephaestus / 角色
  - Independent Verif: 验证 / 复验 / 独立 / 不信
  - ultrawork 契约    : ultrawork / 不完成不停止 / todo

DSH 工具调用层（tool-todo / tool-subagent 真实执行）留给用户在本地 DSH 真跑
（见 adapters/dsh/README.md 的 PoC 快速开始）。
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TRIGGER = ROOT / "adapters" / "dsh" / "ultrawork-trigger.md"
OLLAMA = "http://localhost:11434/api/chat"
MODEL = "qwen3.5:4b"

def extract_system_prompt(trigger_md: str) -> str:
    # 取第一个 --- 与最后一个 --- 之间的内容作为 system 提示词
    parts = trigger_md.split("\n---\n", 2)
    if len(parts) >= 2:
        return parts[1].strip()
    return trigger_md  # fallback：整篇

def main():
    trigger = TRIGGER.read_text(encoding="utf-8")
    system_prompt = extract_system_prompt(trigger)
    user_task = "ultrawork 在 ./demo 目录建一个 Node.js hello-world 项目，写测试，跑通自检"

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_task},
        ],
        "think": False,
        "stream": False,
        "options": {"num_ctx": 16384, "temperature": 0.4},
    }

    print(f"[PoC] model={MODEL} system_prompt={len(system_prompt)} chars user_task={user_task!r}")
    print(f"[PoC] calling {OLLAMA} ...")

    req = urllib.request.Request(
        OLLAMA,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print(f"[PoC] FAILED: {e}")
        sys.exit(1)

    content = data.get("message", {}).get("content", "")
    eval_tokens = data.get("eval_count", "?")
    dur = data.get("total_duration", 0) / 1e9 if data.get("total_duration") else 0

    print(f"[PoC] response {len(content)} chars, {eval_tokens} eval tokens, {dur:.1f}s\n")
    print("=" * 70)
    print(content)
    print("=" * 70)

    # 关键词命中评估
    kw = {
        "Intent Gate": [r"意图", r"intent", r"真实意图"],
        "Codebase Assessment": [r"架构", r"评估", r"摸", r"explore", r"grep", r"glob"],
        "Smart Delegation": [r"委派", r"category", r"subagent", r"hephaestus", r"oracle", r"角色"],
        "Independent Verification": [r"验证", r"复验", r"独立", r"不信"],
        "ultrawork 契约": [r"ultrawork", r"不完成不停止", r"todo", r"boulder"],
    }
    print("\n[PoC] 阶段命中评估：")
    hit = 0
    for phase, patterns in kw.items():
        ok = any(re.search(p, content, re.IGNORECASE) for p in patterns)
        mark = "✅" if ok else "❌"
        if ok:
            hit += 1
        print(f"  {mark} {phase}")
    print(f"\n[PoC] 命中 {hit}/5 阶段  ->  {'PASS (大脑层可行)' if hit >= 4 else 'PARTIAL (提示词需调)' if hit >= 2 else 'FAIL'}")

    # 存输出
    out = ROOT / "examples" / "poc-output.md"
    out.write_text(
        f"# omo-bridge PoC 输出（DSH adapter 大脑层）\n\n"
        f"- model: `{MODEL}`\n- eval_tokens: {eval_tokens}\n- duration: {dur:.1f}s\n"
        f"- 阶段命中: {hit}/5\n\n"
        f"## 任务\n\n{user_task}\n\n## 模型响应\n\n```\n{content}\n```\n",
        encoding="utf-8",
    )
    print(f"[PoC] output saved -> {out}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
omo-bridge / examples / analyze-dsh-session.py

通用 DSH session 分析器。输入 session.jsonl（已解压）或 session.jsonl.zstd（自动流式解压），
按 step 打印 assistant message + tool call + todo + tool result 摘要，并标注 stopReason
检测 tool call 退化（stop vs toolUse）。

用法：
  python analyze-dsh-session.py <session.jsonl 或 .jsonl.zstd 路径>

复用：v1 / v2 / 任何 dsh headless PoC 的执行轨迹分析。
"""
import json
import sys
from pathlib import Path


def maybe_decompress(path: Path) -> bytes:
    if path.suffix == ".zstd" or path.name.endswith(".jsonl.zstd"):
        try:
            import zstandard as z
            d = z.ZstdDecompressor()
            with open(path, "rb") as f:
                with d.stream_reader(f) as r:
                    return r.read()
        except ImportError:
            sys.exit("ERROR: 需要 zstandard 包。pip install zstandard")
    return path.read_bytes()


def main():
    if len(sys.argv) < 2:
        sys.exit("用法: python analyze-dsh-session.py <session.jsonl|.jsonl.zstd>")
    path = Path(sys.argv[1])
    data = maybe_decompress(path)
    lines = data.decode("utf-8", errors="replace").splitlines()

    print(f"=== session: {path.name} ({len(lines)} lines) ===\n")
    degeneration = []
    step = 0
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except Exception:
            continue
        t = o.get("type")
        data_o = o.get("data", {})
        if t == "step/start":
            step = data_o.get("step", "?")
            print(f"\n--- STEP {step} (line {i}) ---")
        elif t == "assistant/message":
            msg = data_o.get("message", {})
            src = msg.get("source", {})
            replay = src.get("replayState", {})
            stop = replay.get("stopReason", "?")
            model = src.get("model", "?")
            content = msg.get("content", [])
            parts = []
            for c in content:
                ct = c.get("type")
                if ct == "reasoning":
                    parts.append(f"[REASONING] {c.get('text','')[:150]}")
                elif ct == "tool-call":
                    parts.append(f"[TOOL-CALL] {c.get('name')} args={c.get('arguments','')[:150]}")
                elif ct == "text":
                    parts.append(f"[TEXT] {c.get('text','')[:200]}")
                else:
                    parts.append(f"[{ct}] {str(c)[:100]}")
            usage = data_o.get("usage", {})
            print(f"  ASSISTANT step={data_o.get('step')} stop={stop} model={model} "
                  f"in={usage.get('inputTokens','?')} out={usage.get('outputTokens','?')}")
            for p in parts:
                print(f"    {p}")
            # 退化检测：stop 而非 toolUse，且 reasoning 里有 {"name": 字样
            if stop == "stop":
                reasoning_text = " ".join(c.get("text", "") for c in content if c.get("type") == "reasoning")
                if '"name"' in reasoning_text and "arguments" in reasoning_text:
                    degeneration.append((step, i, usage.get("inputTokens")))
                    print(f"    ⚠️ TOOL-CALL DEGENERATION: stop=stop, tool call written as text in reasoning")
        elif t == "tool/call":
            print(f"  TOOL_CALL: {data_o.get('name')} args={data_o.get('arguments','')[:200]}")
        elif t == "todo/write":
            todos = data_o.get("todos", [])
            statuses = [(t.get("status"), t.get("content", "")[:40]) for t in todos]
            print(f"  TODO: {statuses}")
        elif t == "tool/result":
            content = data_o.get("message", {}).get("content", [])
            txt = ""
            for c in content:
                for sub in c.get("content", []):
                    txt = sub.get("text", "")[:150]
            is_err = any(c.get("isError") for c in content)
            print(f"  TOOL_RESULT{'(ERR)' if is_err else ''}: {txt}")
        elif t == "turn/end":
            reason = data_o.get("reason", {})
            print(f"\n=== TURN END: {reason.get('kind','?')} ===")

    print("\n=== 退化检测 ===")
    if degeneration:
        for s, ln, tk in degeneration:
            print(f"  ⚠️ step {s} (line {ln}, inputTokens={tk}): tool call 退化为文本")
    else:
        print("  ✅ 无 tool call 退化")


if __name__ == "__main__":
    main()

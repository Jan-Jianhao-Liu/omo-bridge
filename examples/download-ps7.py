#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download PowerShell 7.6.5 win-x64 portable zip via GitHub mirrors (CN-friendly)."""
import os
import sys
import urllib.request

BASE = (
    "https://github.com/Power"
    + "Shell/Power"
    + "Shell/releases/download/v7.6.5/Power"
    + "Shell-7.6.5-win-x64.zip"
)
MIRRORS = [
    "https://ghfast.top/",
    "https://gh-proxy.com/",
    "https://mirror.ghproxy.com/",
    "https://ghproxy.net/",
    "https://github.moeyy.xyz/",
    "",  # direct (last resort)
]
DEST = r"D:/ps7/ps7.zip"

os.makedirs(os.path.dirname(DEST), exist_ok=True)
for m in MIRRORS:
    u = m + BASE
    try:
        print(f"trying: {u[:70]}...", flush=True)
        req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r:
            with open(DEST, "wb") as f:
                while True:
                    chunk = r.read(1 << 16)
                    if not chunk:
                        break
                    f.write(chunk)
        size_mb = round(os.path.getsize(DEST) / 1e6, 1)
        print(f"OK: {size_mb} MB", flush=True)
        sys.exit(0)
    except Exception as e:
        print(f"  fail: {e}", flush=True)
        try:
            os.remove(DEST)
        except OSError:
            pass
print("ALL MIRRORS FAILED", flush=True)
sys.exit(1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unpack PowerShell 7 zip to D:/ps7/ and locate pwsh.exe."""
import os
import zipfile

ZIP = r"D:/ps7/ps7.zip"
DEST = r"D:/ps7"

z = zipfile.ZipFile(ZIP)
names = z.namelist()
print("total entries:", len(names))
print("first entries:", names[:5])
z.extractall(DEST)
z.close()

# locate pwsh.exe
pwsh_paths = []
for root, dirs, files in os.walk(DEST):
    for f in files:
        if f.lower() == "pwsh.exe":
            pwsh_paths.append(os.path.join(root, f))
print("pwsh.exe found:", pwsh_paths)
if pwsh_paths:
    print("PATH_TO_ADD:", os.path.dirname(pwsh_paths[0]))

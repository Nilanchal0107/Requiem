"""Fails if a tracked file has no owner, or more than one, in v2-file-map.md.

Run: uv run python .scratch/v1-skeleton/check_file_map.py
"""
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

MAP = Path(__file__).with_name("v2-file-map.md")

# rows of the Owners table: | `pattern` | Owner | `except`, `except` |
rows = []
owners = MAP.read_text(encoding="utf-8").split("## Owners")[1].split("\n## ")[0]
for line in owners.splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) == 3 and cells[0].startswith("`"):
        rows.append((cells[0].strip("`"), cells[1], re.findall(r"`([^`]+)`", cells[2])))

files = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout.splitlines()
problems = []
for f in files:
    hits = [owner for pat, owner, excepts in rows if fnmatch(f, pat) and not any(fnmatch(f, e) for e in excepts)]
    if len(hits) != 1:
        problems.append(f"{f}: {hits or 'no owner'}")

assert rows, "no rows parsed from the Owners table"
print(f"{len(files)} tracked files, {len(rows)} rows")
print("\n".join(problems) or "every file has exactly one owner")
sys.exit(1 if problems else 0)

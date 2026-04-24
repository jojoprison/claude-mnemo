#!/usr/bin/env python3
"""Scan Claude Code session JSONL for tool usage, skills, files modified, commits.

Reads CLAUDE_SESSION_ID from env, locates the matching .jsonl in
~/.claude/projects/*/SESSION_ID.jsonl, prints a compact summary.

Cached to /tmp/mnemo-session-scan-{SESSION_ID}.json for 60s to keep
session-review reruns fast during a single review cycle.
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time


def find_jsonl(session_id: str) -> str | None:
    home = os.path.expanduser("~")
    for d in glob.glob(os.path.join(home, ".claude/projects/*/")):
        candidate = os.path.join(d, session_id + ".jsonl")
        if os.path.exists(candidate):
            return candidate
    return None


def scan(jsonl_path: str) -> dict:
    tools: dict[str, int] = {}
    skills: list[str] = []
    commits = 0
    files_written: set[str] = set()
    errors = 0

    with open(jsonl_path) as f:
        for line in f:
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            content = msg.get("message", {}).get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "tool_use":
                    name = block.get("name", "")
                    tools[name] = tools.get(name, 0) + 1
                    inp = block.get("input", {})
                    if name == "Skill":
                        s = inp.get("skill", "")
                        if s:
                            skills.append(s)
                    elif name in ("Write", "Edit"):
                        fp = inp.get("file_path", "")
                        if fp:
                            files_written.add(fp)
                    elif name == "Bash":
                        cmd = inp.get("command", "")
                        if "git commit" in cmd:
                            commits += 1
                elif btype == "tool_result" and block.get("is_error"):
                    errors += 1

    return {
        "tools": tools,
        "skills": skills,
        "commits": commits,
        "files_written": sorted(files_written),
        "errors": errors,
    }


def render(result: dict) -> None:
    tools = result["tools"]
    print(f"TOTAL_TOOL_CALLS: {sum(tools.values())}")
    for t, c in sorted(tools.items(), key=lambda x: -x[1])[:20]:
        print(f"  {t}: {c}")
    skills = result["skills"]
    print(f"\nSKILLS_INVOKED: {', '.join(skills) if skills else 'none'}")
    files_written = result["files_written"]
    print(f"FILES_MODIFIED: {len(files_written)}")
    if files_written:
        exts: dict[str, int] = {}
        for fp in files_written:
            ext = os.path.splitext(fp)[1] or "no-ext"
            exts[ext] = exts.get(ext, 0) + 1
        exts_str = ", ".join(f"{e}({c})" for e, c in sorted(exts.items(), key=lambda x: -x[1]))
        print(f"  Extensions: {exts_str}")
        for fp in files_written[:15]:
            print(f"  {fp}")
    print(f"COMMITS: {result['commits']}")
    print(f"ERRORS_SEEN: {result['errors']}")


def main() -> int:
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    if not session_id:
        print("SESSION_ID: not available")
        return 0

    cache_path = f"/tmp/mnemo-session-scan-{session_id}.json"
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) < 60:
        with open(cache_path) as f:
            render(json.load(f))
        return 0

    jsonl_path = find_jsonl(session_id)
    if not jsonl_path:
        print("JSONL: not found — use conversation context for analysis")
        return 0

    result = scan(jsonl_path)
    try:
        with open(cache_path, "w") as f:
            json.dump(result, f)
    except OSError:
        pass
    render(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

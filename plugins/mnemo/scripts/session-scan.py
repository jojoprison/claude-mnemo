#!/usr/bin/env python3
"""Scan Claude Code session JSONL for tool usage, skills, files modified, commits.

Reads CLAUDE_SESSION_ID from env, locates the matching .jsonl in
~/.claude/projects/*/SESSION_ID.jsonl, prints a compact summary.

Two-layer caching:
- Fresh cache (<60s old) → reuse as-is, no re-read.
- Older cache + stored byte offset → read only appended JSONL bytes since
  offset, merge into cached aggregate. Works because JSONL is append-only.

Files under /tmp/:
- mnemo-session-scan-{id}.json — aggregated result
- mnemo-session-offset-{id}.json — {"offset": N, "mtime": ...}
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time


FRESH_TTL = 60  # seconds


def find_jsonl(session_id: str) -> str | None:
    home = os.path.expanduser("~")
    for d in glob.glob(os.path.join(home, ".claude/projects/*/")):
        candidate = os.path.join(d, session_id + ".jsonl")
        if os.path.exists(candidate):
            return candidate
    return None


def empty_acc() -> dict:
    return {
        "tools": {},
        "skills": [],
        "commits": 0,
        "files_written": [],
        "errors": 0,
    }


def parse_lines(handle, acc: dict) -> None:
    """Accumulate counts from each JSONL line. Modifies acc in place."""
    tools = acc["tools"]
    skills = acc["skills"]
    files_written = set(acc["files_written"])

    for line in handle:
        line = line.strip()
        if not line:
            continue
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
                        acc["commits"] = acc.get("commits", 0) + 1
            elif btype == "tool_result" and block.get("is_error"):
                acc["errors"] = acc.get("errors", 0) + 1

    acc["files_written"] = sorted(files_written)


def scan_incremental(jsonl_path: str, session_id: str) -> dict:
    cache_path = f"/tmp/mnemo-session-scan-{session_id}.json"
    offset_path = f"/tmp/mnemo-session-offset-{session_id}.json"

    prev_acc: dict | None = None
    prev_offset = 0

    if os.path.exists(cache_path) and os.path.exists(offset_path):
        try:
            with open(cache_path) as f:
                prev_acc = json.load(f)
            with open(offset_path) as f:
                prev_offset = int(json.load(f).get("offset", 0))
        except (OSError, ValueError, json.JSONDecodeError):
            prev_acc = None
            prev_offset = 0

    try:
        file_size = os.path.getsize(jsonl_path)
    except OSError:
        return prev_acc or empty_acc()

    # Previous offset beyond file size → file rotated / truncated; re-scan from 0.
    if prev_offset > file_size:
        prev_acc = None
        prev_offset = 0

    acc = prev_acc if prev_acc is not None else empty_acc()

    with open(jsonl_path) as f:
        f.seek(prev_offset)
        parse_lines(f, acc)
        new_offset = f.tell()

    try:
        with open(cache_path, "w") as f:
            json.dump(acc, f)
        with open(offset_path, "w") as f:
            json.dump({"offset": new_offset, "mtime": time.time()}, f)
    except OSError:
        pass

    return acc


def render(result: dict) -> None:
    tools = result.get("tools", {})
    print(f"TOTAL_TOOL_CALLS: {sum(tools.values())}")
    for t, c in sorted(tools.items(), key=lambda x: -x[1])[:20]:
        print(f"  {t}: {c}")
    skills = result.get("skills", [])
    print(f"\nSKILLS_INVOKED: {', '.join(skills) if skills else 'none'}")
    files_written = result.get("files_written", [])
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
    print(f"COMMITS: {result.get('commits', 0)}")
    print(f"ERRORS_SEEN: {result.get('errors', 0)}")


def main() -> int:
    session_id = os.environ.get("CLAUDE_SESSION_ID", "")
    if not session_id:
        print("SESSION_ID: not available")
        return 0

    cache_path = f"/tmp/mnemo-session-scan-{session_id}.json"
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) < FRESH_TTL:
        try:
            with open(cache_path) as f:
                render(json.load(f))
            return 0
        except (OSError, json.JSONDecodeError):
            pass  # fall through to re-scan

    jsonl_path = find_jsonl(session_id)
    if not jsonl_path:
        print("JSONL: not found — use conversation context for analysis")
        return 0

    result = scan_incremental(jsonl_path, session_id)
    render(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())

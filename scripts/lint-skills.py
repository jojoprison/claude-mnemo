#!/usr/bin/env python3
"""Validate every SKILL.md in plugins/*/skills/*/SKILL.md.

Checks:
1. Frontmatter parses (YAML between --- markers).
2. Required fields present: name, description.
3. model field (if present) is in whitelist: haiku, sonnet, opus.
4. File length ≤ 500 lines (skill-creator best practice).
5. Any `references/*.md` path mentioned in the body actually exists.
6. Any `scripts/*.{sh,py}` path mentioned resolves to an existing file.
7. Any `assets/*` path mentioned resolves.

Exit codes:
  0 — all SKILL.md valid
  1 — one or more violations found
"""
from __future__ import annotations

import glob
import os
import re
import sys


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MODEL_WHITELIST = {"haiku", "sonnet", "opus"}
MAX_LINES = 500
REF_RE = re.compile(r"references/([a-zA-Z0-9_\-]+\.md)")
SCRIPT_RE = re.compile(r"scripts/([a-zA-Z0-9_\-]+\.(?:sh|py))")
ASSET_RE = re.compile(r"assets/([a-zA-Z0-9_\-.]+)")


def parse_frontmatter(text: str) -> tuple[dict[str, str] | None, str]:
    if not text.startswith("---\n"):
        return None, "no opening --- marker"
    end = text.find("\n---\n", 4)
    if end == -1:
        return None, "no closing --- marker"
    fm_raw = text[4:end]
    fm: dict[str, str] = {}
    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, ""


def check_skill(path: str) -> list[str]:
    issues: list[str] = []
    try:
        with open(path) as f:
            text = f.read()
    except OSError as e:
        return [f"cannot read: {e}"]

    lines = text.count("\n") + 1
    if lines > MAX_LINES:
        issues.append(f"{lines} lines > {MAX_LINES} (progressive disclosure: extract to references/)")

    fm, err = parse_frontmatter(text)
    if fm is None:
        issues.append(f"frontmatter: {err}")
        return issues

    for required in ("name", "description"):
        if required not in fm:
            issues.append(f"frontmatter missing required field: {required}")

    model = fm.get("model")
    if model and model not in MODEL_WHITELIST:
        issues.append(f"model '{model}' not in whitelist {sorted(MODEL_WHITELIST)}")

    plugin_dir = os.path.dirname(os.path.dirname(os.path.dirname(path)))
    for match in REF_RE.finditer(text):
        ref_name = match.group(1)
        ref_path = os.path.join(plugin_dir, "references", ref_name)
        if not os.path.exists(ref_path):
            issues.append(f"references/{ref_name} referenced but file missing")

    for match in SCRIPT_RE.finditer(text):
        script_name = match.group(1)
        script_path = os.path.join(plugin_dir, "scripts", script_name)
        if not os.path.exists(script_path):
            issues.append(f"scripts/{script_name} referenced but file missing")

    for match in ASSET_RE.finditer(text):
        asset_name = match.group(1)
        asset_path = os.path.join(plugin_dir, "assets", asset_name)
        if not os.path.exists(asset_path):
            issues.append(f"assets/{asset_name} referenced but file missing")

    return issues


def main() -> int:
    pattern = os.path.join(REPO_ROOT, "plugins", "*", "skills", "*", "SKILL.md")
    skills = sorted(glob.glob(pattern))
    if not skills:
        print(f"No SKILL.md found under {pattern}")
        return 1

    had_issues = False
    for path in skills:
        rel = os.path.relpath(path, REPO_ROOT)
        issues = check_skill(path)
        if issues:
            had_issues = True
            print(f"\n❌ {rel}")
            for issue in issues:
                print(f"   • {issue}")
        else:
            print(f"✅ {rel}")

    print()
    if had_issues:
        print("LINT FAILED — fix the issues above.")
        return 1
    print(f"LINT PASSED — {len(skills)} SKILL.md files, zero violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

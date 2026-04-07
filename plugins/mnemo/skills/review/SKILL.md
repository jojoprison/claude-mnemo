---
name: review
description: "Use at the end of any session (or when asked 'what did we miss?', 'что забыли', 'session review', 'что осталось', 'all done?') to analyze session completeness. Discovers all available skills, detects what was used vs should have been, offers to execute missed skills in order. Always thorough."
user-invocable: false
---

# mnemo:review — Skill-Aware Session Completeness Analyzer

You are performing a thorough end-of-session review. Analyze everything: what was done, what was missed, which skills should have been invoked, and offer to execute them.

## Session Data (Preprocessed)

### Git State

!`echo "=== STATUS ===" && git status --short 2>/dev/null && echo "=== BRANCH ===" && git branch --show-current 2>/dev/null && echo "=== LOG ===" && git log --oneline -10 2>/dev/null && echo "=== UNCOMMITTED ===" && git diff --stat 2>/dev/null && echo "=== STAGED ===" && git diff --staged --stat 2>/dev/null`

### Open PRs

!`gh pr list --author @me --state open --json number,title,url 2>/dev/null || echo "gh: not available"`

### Tools & Skills Used This Session

!`python3 << 'PYEOF'
import json, sys, os, glob

session_id = '${CLAUDE_SESSION_ID}'
if not session_id or '${' in session_id:
    print('SESSION_ID: not available')
    sys.exit(0)

home = os.path.expanduser('~')
jsonl_path = None
for d in glob.glob(os.path.join(home, '.claude/projects/*/')):
    candidate = os.path.join(d, session_id + '.jsonl')
    if os.path.exists(candidate):
        jsonl_path = candidate
        break

if not jsonl_path:
    print('JSONL: not found — use conversation context for analysis')
    sys.exit(0)

tools = {}
skills = []
commits = 0
files_written = set()
errors = 0

with open(jsonl_path) as f:
    for line in f:
        try:
            msg = json.loads(line)
            content = msg.get('message', {}).get('content', [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use':
                    name = block.get('name', '')
                    tools[name] = tools.get(name, 0) + 1
                    inp = block.get('input', {})
                    if name == 'Skill':
                        s = inp.get('skill', '')
                        if s:
                            skills.append(s)
                    elif name in ('Write', 'Edit'):
                        fp = inp.get('file_path', '')
                        if fp:
                            files_written.add(fp)
                    elif name == 'Bash':
                        cmd = inp.get('command', '')
                        if 'git commit' in cmd:
                            commits += 1
                elif block.get('type') == 'tool_result' and block.get('is_error'):
                    errors += 1
        except:
            continue

print(f'TOTAL_TOOL_CALLS: {sum(tools.values())}')
for t, c in sorted(tools.items(), key=lambda x: -x[1])[:20]:
    print(f'  {t}: {c}')
print(f'\nSKILLS_INVOKED: {", ".join(skills) if skills else "none"}')
print(f'FILES_MODIFIED: {len(files_written)}')
if files_written:
    exts = {}
    for fp in files_written:
        ext = os.path.splitext(fp)[1] or 'no-ext'
        exts[ext] = exts.get(ext, 0) + 1
    print(f'  Extensions: {", ".join(f"{e}({c})" for e, c in sorted(exts.items(), key=lambda x: -x[1]))}')
    for fp in sorted(files_written)[:15]:
        print(f'  {fp}')
print(f'COMMITS: {commits}')
print(f'ERRORS_SEEN: {errors}')
PYEOF
`

### All Available Skills (Auto-Discovered)

!`python3 << 'PYEOF'
import os, glob, re

home = os.path.expanduser('~')
skills = []
seen = set()

patterns = [
    os.path.join(home, '.claude/skills/*/SKILL.md'),
    os.path.join(home, '.claude/plugins/*/skills/*/SKILL.md'),
    os.path.join(home, '.claude/plugins/cache/*/*/*/skills/*/SKILL.md'),
    os.path.join(home, '.claude/plugins/marketplaces/*/plugins/*/skills/*/SKILL.md'),
    '.claude/skills/*/SKILL.md',
    'plugins/*/skills/*/SKILL.md',
]

for pat in patterns:
    for path in glob.glob(pat):
        if path in seen:
            continue
        seen.add(path)
        try:
            with open(path) as f:
                head = f.read(600)
            name_m = re.search(r'^name:\s*["\']?(.+?)["\']?\s*$', head, re.M)
            desc_m = re.search(r'^description:\s*["\']?(.+?)["\']?\s*$', head, re.M)
            if not name_m:
                continue
            name = name_m.group(1).strip()
            desc = desc_m.group(1).strip()[:100] if desc_m else ''

            parts = path.replace(home, '~').split('/')
            plugin = ''
            if 'plugins' in parts:
                idx = parts.index('plugins')
                candidate = parts[idx + 1] if idx + 1 < len(parts) else ''
                if candidate == 'marketplaces' and idx + 3 < len(parts):
                    plugin = parts[idx + 3]
                else:
                    plugin = candidate

            qualified = f'{plugin}:{name}' if plugin else name
            if qualified not in seen:
                seen.add(qualified)
                skills.append(f'{qualified} — {desc}')
        except:
            continue

skills.sort()
for s in skills:
    print(s)
print(f'\nTOTAL_SKILLS: {len(skills)}')
PYEOF
`

$ARGUMENTS

## Workflow

### Step 1: Load Project Context

Read CLAUDE.md for project-specific rules:

```bash
cat CLAUDE.md 2>/dev/null | head -300
```

Check memory index:
```bash
cat .claude/projects/*/memory/MEMORY.md 2>/dev/null | head -100
```

### Step 2: Determine Session Type

Classify by primary activity using preprocessed data + conversation history:

| Type | Key signals |
|------|-------------|
| **Implementation** | Write/Edit heavy, commits, new files, "feat/add" keywords |
| **Research** | Read/Grep/WebSearch/Agent heavy, few writes |
| **Debugging** | Error patterns, "fix" commits, investigation flow |
| **Refactoring** | Renames, large diffs, net-zero line changes |
| **Documentation** | .md files dominant, few code changes |
| **Configuration** | Config/CI/deploy files changed |
| **Planning** | Plan mode, brainstorm docs, no code |

State the detected type explicitly.

### Step 3: Full Session Scan

From conversation history + preprocessed data, identify:

1. **User requests** — all explicit and implicit asks. Were they all fulfilled?
2. **Decisions made** — architecture, approach, scope choices. Were they saved?
3. **Actions completed** — commits, PRs, file changes, deployments
4. **TODOs mentioned** — "потом", "later", "TODO", "FIXME" in conversation or code
5. **Errors encountered** — all resolved? Workarounds or proper fixes?
6. **Questions asked** — by user or Claude, answered or dropped?
7. **External systems** — Linear tasks, GitHub PRs, Obsidian notes — updated?

### Step 4: Skill Gap Analysis

Cross-reference:
- **Session type** (Step 2) → expected skill categories
- **Signals detected** (Step 3) → specific skill triggers
- **Skills already invoked** (preprocessed SKILLS_INVOKED)
- **All available skills** (preprocessed auto-discovery)

**CRITICAL: Only recommend skills that appear in the auto-discovered list.** Never recommend skills that aren't installed.

#### Trigger Matrix by Session Type

**Implementation sessions:**

| Signal | Recommended skill | Priority |
|--------|------------------|----------|
| New code without corresponding tests | test-master, test-driven-development | CRITICAL |
| Web app code (.html/.tsx/.jsx/.css) | vibesec, design-review | HIGH |
| Diff > 100 lines, single feature | simplify | MEDIUM |
| Branch diverged from main, tests pass | ship | HIGH |
| API endpoints added or changed | api-designer | MEDIUM |
| Django models/views touched | django-expert | MEDIUM |
| Rails code touched | dhh-rails-style | MEDIUM |
| Database migrations in diff | postgres-pro, data-integrity-guardian | HIGH |
| Frontend components modified | design-review, polish | MEDIUM |

**Research sessions:**

| Signal | Recommended skill | Priority |
|--------|------------------|----------|
| Findings/discoveries not saved | mnemo:save | CRITICAL |
| No session summary created | mnemo:session | HIGH |
| New knowledge links to existing notes | mnemo:connect | MEDIUM |

**Debugging sessions:**

| Signal | Recommended skill | Priority |
|--------|------------------|----------|
| Root cause identified (save as gotcha) | mnemo:save | HIGH |
| Fix committed without regression tests | test-master | CRITICAL |
| Investigation log worth preserving | mnemo:session | MEDIUM |

**All sessions (universal triggers):**

| Signal | Recommended skill | Priority |
|--------|------------------|----------|
| Significant work done, no session notes | mnemo:session | HIGH |
| Decisions in conversation, not persisted | mnemo:save | HIGH |
| Uncommitted changes in working tree | commit | CRITICAL |
| Branch ready, no PR created | ship | HIGH |
| Project has memory routing rules (CLAUDE.md) | check all memory backends | MEDIUM |
| New Obsidian notes created this session | mnemo:connect, mnemo:health | LOW |
| Plan created but not reviewed | plan-eng-review, plan-ceo-review | MEDIUM |
| Code written, no review pass | review, ce:review | MEDIUM |
| CLAUDE.md needs updating | claude-md-management:revise-claude-md | LOW |

Also check for custom triggers:
```bash
cat "${CLAUDE_SKILL_DIR}/skill-triggers.md" 2>/dev/null
```

### Step 5: Cross-Reference Project Rules

From CLAUDE.md, check mandatory steps:

| Rule category | What to check |
|---------------|--------------|
| Git flow | PR created? Correct format? Draft or ready? |
| CI checks | Tests run? Lint passing? Type-check? |
| Memory routing | All required backends updated? (Obsidian, claude-mem, memory/) |
| Session handoff | Handoff note updated in Obsidian? |
| Task tracker | Linear/GitHub issue status moved? PR linked? |
| Documentation | README/docs match code changes? |
| Stop-rules | Any project-specific rules violated? |

### Step 6: Generate Report

**Respond in the user's language** (match conversation language).

**BLUF: score first, then details.**

```markdown
## Session Review

**Project:** {name}
**Branch:** {branch}
**Type:** {session type}
**Task:** {one-line summary}

### Done ({count})

| # | What | Evidence |
|---|------|----------|
| 1 | {item} | {commit hash / PR / file path} |

### Missed ({count})

| # | What | Priority | Action |
|---|------|----------|--------|
| 1 | {item} | CRITICAL | {specific action} |

### Hanging Threads ({count})

| # | What | Where mentioned | Next step |
|---|------|----------------|-----------|
| 1 | {item} | {context} | {action} |

### Skill Gap

**Invoked this session:** {list, or "none"}

**Should have been invoked:**

| # | Skill | Why | Priority |
|---|-------|-----|----------|
| 1 | /mnemo:session | Significant work done, no session notes | HIGH |

**Correctly skipped:** {skills matching signals but rightly unused, with reason}

### Score: {X}/10

| Dimension | Status | Detail |
|-----------|--------|--------|
| Code | {status} | |
| Tests | {status} | |
| Memory | {status} | |
| Docs | {status} | |
| PR / Git | {status} | |
| Skills | {used/recommended} | |
```

### Step 7: Execute Missed Skills

After the report, offer to run recommended skills **in priority order**:

```
{N} skills recommended. Execute?

Execution plan (priority order):
  1. [CRITICAL] /commit — uncommitted changes
  2. [HIGH] /mnemo:save — {N} unsaved decisions
  3. [HIGH] /mnemo:session — session notes
  4. [MEDIUM] /simplify — cleanup pass

Options:
  A — Execute all in order
  1,2,3... — Execute specific ones
  N — Skip
```

**Execution rules:**
1. Run skills sequentially using the Skill tool
2. Brief status after each
3. Dependency order: /commit before /ship, /mnemo:save before /mnemo:session
4. After all done, output updated score

## Rules

- **Always thorough** — full analysis, no shortcuts
- **BLUF** — score and critical items first
- **Be specific** — "3 unsaved decisions: X, Y, Z" not "maybe save something"
- **Don't nag** — skill already ran per SKILLS_INVOKED? Skip it
- **Don't hallucinate skills** — only recommend from auto-discovered list
- **Project rules override** — CLAUDE.md > generic recommendations
- **Execution order** — commit → review → ship → session → save
- **User's language** — match conversation
- **Preprocessing fallback** — if JSONL/discovery failed, gather data with Bash at runtime
- **Don't over-report** — unchecked plan AC is noise if code + tests pass
- **Multiple projects** — analyze each project dir separately
- **Respect completed work** — /mnemo:save already ran? Acknowledge, don't re-recommend

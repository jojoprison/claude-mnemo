# mnemo:review — Skill-Aware Session Completeness Analyzer

## Overview

End-of-session review that goes beyond "what was done" — it knows which skills exist in your system, which ones were used, and which ones you should have used. Then offers to run them.

## Usage

```
/mn:review
```

Also triggers on: "что забыли?", "что осталось?", "session review", "all done?", "what did we miss?"

## How It Works

### 1. Preprocessing (before Claude sees the prompt)

Shell scripts run automatically:
- **Git state** — status, branch, recent commits, uncommitted changes
- **JSONL introspection** — parses `${CLAUDE_SESSION_ID}.jsonl` to extract every tool call, skill invocation, modified file, error count
- **Skill discovery** — globs 6 paths to find all 200+ installed skills across personal skills, plugins, cache, and marketplaces
- **Open PRs** — checks for your open GitHub PRs

### 2. Session fingerprinting

Classifies the session based on tool usage patterns:

| Type | Key signals |
|------|-------------|
| Implementation | Write/Edit heavy, commits, "feat/add" |
| Research | Read/Grep/WebSearch heavy, few writes |
| Debugging | Error patterns, "fix" commits |
| Refactoring | Renames, large diffs |
| Documentation | .md files dominant |
| Configuration | Config/CI/deploy files |
| Planning | Plan mode, brainstorm docs |

### 3. Skill gap analysis

Cross-references session type → signals → available skills → already used skills. Only recommends skills that are **actually installed**.

Examples:
- Implementation session + no tests → recommends `/test-master`
- Research session + no notes saved → recommends `/mn:save`, `/mn:session`
- Branch diverged + no PR → recommends `/ship`

### 4. Execution chain

Offers to run missed skills in priority order:

```
3 skills recommended. Execute?

  1. [CRITICAL] /commit — uncommitted changes
  2. [HIGH] /mn:save — 3 unsaved decisions
  3. [HIGH] /mn:session — session notes

Options:
  A — Execute all in order
  1,2,3 — Execute specific ones
  N — Skip
```

## Example Output

```
## Session Review

Project: claude-mnemo
Branch: main
Type: Implementation
Task: Plugin refactoring — naming, review rewrite

### Done (4)
| # | What | Evidence |
|---|------|----------|
| 1 | Plugin rename mn→mnemo | plugin.json |
| 2 | Review SKILL.md rewrite | 350+ lines |

### Missed (2)
| # | What | Priority | Action |
|---|------|----------|--------|
| 1 | Uncommitted changes | CRITICAL | git commit |
| 2 | Session notes | HIGH | /mn:session |

### Skill Gap
Used: mn:ask
Should use: /mn:session, /mn:save

### Score: 5/10
```

## Important Notes

- **Always thorough** — no quick mode, full analysis every time
- **Inline execution** — runs in main conversation context, can invoke other skills
- **BLUF** — score and critical items first, details below
- **Won't nag** — if a skill already ran this session, skips it
- **Only recommends installed skills** — never suggests unavailable tools

## Related Skills

- `/mn:session` — often recommended by review as a missed skill
- `/mn:save` — often recommended for unsaved decisions
- `/mn:health` — review may suggest if new Obsidian notes were created

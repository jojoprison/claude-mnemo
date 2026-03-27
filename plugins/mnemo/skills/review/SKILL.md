---
name: review
description: "Use at the end of any session (or when asked 'what did we miss?', 'что забыли', 'session review', 'что осталось') to analyze the session for completeness. Scans conversation history, project rules, CLAUDE.md, and memory to find: done items, missed items, hanging threads, and follow-up recommendations. Outputs an actionable table."
user-invocable: true
context: fork
model: opus
---

# mnemo:review — Session Completeness Analyzer

Analyze the current session for completeness. Find what was done, what was missed, and what's left hanging. Adapts to the current project's rules, skills, and conventions.

## When to Trigger

- User asks: "что забыли?", "что осталось?", "session review", "all done?", "ничего не пропустили?"
- End of a long session before signing off
- After completing a major feature/PR
- Manually: `/mnemo:review`

## Workflow

### Step 1: Load Project Context

Read project-specific rules and conventions:

```bash
# 1. Project instructions
cat CLAUDE.md 2>/dev/null | head -200

# 2. Memory index
cat .claude/projects/*/memory/MEMORY.md 2>/dev/null | head -100

# 3. Git state
git status --short
git log --oneline -5
git branch --show-current
git diff --stat HEAD~1 2>/dev/null

# 4. Any open PRs from this session
gh pr list --author @me --state open --json number,title,url 2>/dev/null | head -20

# 5. Linear tasks in progress (if available)
# Check .mcp.json for linear config
```

### Step 2: Scan Session History

Analyze the full conversation for:

1. **User requests** — everything the user asked for (explicitly or implicitly)
2. **Decisions made** — architecture, approach, scope choices
3. **Actions taken** — commits, PRs, file changes, deployments, memory saves
4. **Questions asked by Claude** — were they all answered? Did any answer get lost?
5. **Skills/commands invoked** — /ce:plan, /ce:work, /ce:review, etc.
6. **TODOs mentioned** — in conversation, in plans, in code comments
7. **Errors encountered** — were they all resolved?
8. **External system interactions** — Linear tasks, GitHub PRs, Obsidian notes

### Step 3: Cross-Reference with Project Rules

Check CLAUDE.md for mandatory steps that may have been skipped:

| Rule | Check |
|------|-------|
| Git flow (PR, draft, squash) | Was a PR created? Is it draft? |
| CI checks (lint, test, migrations) | Were they all run? |
| Stop-rules (if any) | Were any violated? |
| Memory routing | Was Obsidian + claude-mem + memory/ updated? |
| Session handoff | Was handoff note updated? |
| Task tracker status | Was the task moved to correct status? PR linked? |
| Docs update | Do docs need updating after this change? |

### Step 4: Identify Hanging Threads

Look for patterns that indicate unfinished work:

- "TODO" or "потом" or "позже" or "later" in conversation
- Questions Claude asked that user didn't answer (or vice versa)
- Plans with unchecked acceptance criteria
- Reviews with unresolved findings
- Mentioned but not executed commands
- "we should also..." or "стоит ещё..." suggestions acknowledged but not acted on
- Code comments with TODO/FIXME added during the session

### Step 5: Generate Completeness Report

Output in this format:

```markdown
## Session Review

**Project:** {project name}
**Branch:** {branch}
**Duration:** {approximate from first/last messages}
**Main task:** {one-line summary}

### Done ({count})

| # | What | Evidence |
|---|------|----------|
| 1 | {item} | {commit/PR/file} |

### Missed ({count})

| # | What | Why it matters | Fix |
|---|------|---------------|-----|
| 1 | {item} | {impact if left undone} | {concrete action} |

### Hanging Threads ({count})

| # | What | Context | Next step |
|---|------|---------|-----------|
| 1 | {item} | {where it came up} | {what to do} |

### Recommendations

{2-3 specific suggestions based on project rules and what was built}

### Completeness Score

{X}/10 — {one-line reason}

Factors:
- Code: {done/total tasks}
- Tests: {passing/total}
- Review: {completed/total rounds}
- Memory: {backends saved to}
- Docs: {updated/needed}
- Task tracker: {status correct?}
- PR: {created? linked?}
```

### Step 6: Offer to Fix

If any "Missed" items can be fixed immediately:

> "Found {N} missed items. Fix now?"
> - A) Fix all now
> - B) Fix critical only
> - C) Just note them for next session

If user chooses A or B — fix immediately. Then re-run the completeness check.

## Adaptation

The skill adapts to ANY project by reading CLAUDE.md at runtime. No hardcoded project rules. It discovers:
- Git flow requirements (branching, PR format, squash policy)
- CI commands (lint, test, type-check)
- Memory systems (Obsidian, claude-mem, memory/, etc.)
- Task trackers (Linear, GitHub Issues)
- Stop-rules and deployment procedures
- Documentation conventions

## Gotchas

- **Don't over-report** — only flag things that matter. Unchecked plan AC is P3, not P1 if code + tests pass.
- **Context compression** — in long sessions, early messages may be truncated. Use git log + file state as ground truth.
- **Multiple projects** — if session touched multiple projects, analyze each separately.
- **Don't duplicate** — if /mnemo:save or /mnemo:session already ran, acknowledge their output.
- **Respect language** — respond in the language the user uses (Russian, English, etc.)

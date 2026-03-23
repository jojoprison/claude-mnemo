---
name: session
description: "Use after completing significant work to write session summary to Obsidian. Triggers after major tasks (features, fixes, research) or manually via /mnemo:session."
user-invocable: true
context: fork
model: opus
---

# mnemo:session — Session Notes to Obsidian

Create a human-readable session summary note in Obsidian after significant work.

## Prerequisites

- **Obsidian must be open**

## Config

Read vault name and handoff note name from `config.json`. Defaults:

```json
{
  "vault": "main",
  "handoff_note": "Meta — Session Handoff"
}
```

## When to Trigger

- After completing a feature / PR / fix
- After significant research session
- Manually via `/mnemo:session`
- Do NOT trigger for trivial tasks (typo fix, one-liner)

## Workflow

### Step 1: Summarize Current Session

Analyze the conversation: what was done, key decisions, commits/PRs created, findings.

### Step 2: Check for Duplicates

```bash
obsidian search query="Session — {YYYY-MM-DD}" vault="{vault}"
```

If session note for today exists, ask: append or create separate?

### Step 3: Create Session Note

```bash
obsidian create name="Session — {YYYY-MM-DD} {short description}" vault="{vault}" content="---
type: session
tags: [session, {project}, {topics}]
date: {YYYY-MM-DD}
branch: {branch-name if exists}
project: {project-name}
---

# Session — {YYYY-MM-DD} {description}

{Brief summary of what was done.}

## What was done
- Item 1
- Item 2

## Key decisions
- Decision 1

## Связи
- [[MOC — {relevant MOC}]]
- [[Related Note 1]]
- [[Ghost Notes for entities]]
"
```

### Step 4: Verify MOC Link

```bash
obsidian read file="{MOC name}" vault="{vault}"
```

Check if the new session note is listed. If not:

```bash
obsidian append file="{MOC name}" vault="{vault}" content="- [[Session — {name}]]"
```

### Step 5: Update Session Handoff

```bash
obsidian read file="{handoff_note}" vault="{vault}"
```

Update with:
- Remove completed pending items from previous sessions
- Add new pending items from current session (if any)
- Update context carry-over section

If handoff note doesn't exist, create it:

```bash
obsidian create name="{handoff_note}" vault="{vault}" content="---
type: meta
tags: [meta, handoff, cross-session]
---

# Meta — Session Handoff

Cross-session continuity file. Read at start of each session, update at end.

## Pending
- [ ] {item} (project: {name}, date: {date})

## Context
- {what happened this session}
"
```

### Step 6: Orphan Check

```bash
obsidian orphans vault="{vault}"
```

If the newly created note appears in orphans, warn the user.

### Step 7: Confirm

Output summary: note name, MOC updated, handoff updated, orphan status.

## Gotchas

- **Obsidian must be open**
- **No session notes for trivial work** — only significant sessions
- **Branch field optional** — research sessions don't have branches
- **Handoff file: APPEND, don't overwrite** — pending items accumulate across sessions
- **Always check duplicate** before creating — same-day sessions may already exist
- **## Связи is mandatory** — at least one MOC link
- **Ghost notes generously** — wrap projects, technologies, people in `[[wikilinks]]`

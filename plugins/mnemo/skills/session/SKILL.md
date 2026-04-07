---
name: session
description: "Use after completing significant work to write session summary to Obsidian. Triggers after major tasks (features, fixes, research) or manually via /mnemo:session."
user-invocable: false
context: fork
model: opus
---

# mnemo:session — Session Notes to Obsidian

Create a human-readable session summary note in Obsidian after significant work.

## Prerequisites

- **Obsidian must be open**

## Config

Read `vault`, `taxonomy.session`, `links_section`, and `handoff_note` from `~/.mnemo/config.json`. If missing, run `/mnemo:setup` or ask user.

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
obsidian search query="{session_prefix}{YYYY-MM-DD}" vault="{vault}"
```

If session note for today exists, ask: append or create separate?

### Step 3: Create Session Note

```bash
obsidian create name="{session_prefix}{YYYY-MM-DD} {short description}" vault="{vault}" content="---
type: session
tags: [session, {project}, {topics}]
date: {YYYY-MM-DD}
branch: {branch-name if exists}
project: {project-name}
---

# {session_prefix}{YYYY-MM-DD} {description}

{Brief summary of what was done.}

## What was done
- Item 1
- Item 2

## Key decisions
- Decision 1

{links_section}
- [[MOC — {relevant MOC}]]
- [[Related Note 1]]
- [[Ghost Notes for entities]]
"
```

Where `{session_prefix}` comes from `config.taxonomy.session.prefix` and `{links_section}` from `config.links_section`.

### Step 4: Verify MOC Link

```bash
obsidian read file="{MOC name}" vault="{vault}"
```

Check if the new session note is listed. If not:

```bash
obsidian append file="{MOC name}" vault="{vault}" content="- [[{session note name}]]"
```

### Step 5: Update Session Handoff

```bash
obsidian read file="{handoff_note}" vault="{vault}"
```

Update with:
- Remove completed pending items from previous sessions
- Add new pending items from current session (if any)
- Update context carry-over section

If handoff note doesn't exist, create it (same as mnemo:setup step 7).

### Step 6: Orphan Check

```bash
obsidian orphans vault="{vault}"
```

If the newly created note appears in orphans, warn the user.

### Step 7: Confirm

Output summary: note name, MOC updated (yes/no), handoff updated, orphan status.

## Gotchas

- **"Unable to connect to main process"** — Obsidian IPC hung. Fix: quit Obsidian (Cmd+Q), reopen, wait 3 seconds, retry

- **Obsidian must be open**
- **No session notes for trivial work** — only significant sessions
- **Branch field optional** — research sessions don't have branches
- **Handoff file: APPEND, don't overwrite** — pending items accumulate across sessions
- **Always check duplicate** before creating — same-day sessions may already exist
- **Links section is mandatory** — at least one MOC link
- **Ghost notes generously** — wrap projects, technologies, people in `[[wikilinks]]`

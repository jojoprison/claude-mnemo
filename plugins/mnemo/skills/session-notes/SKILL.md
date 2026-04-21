---
name: session-notes
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

## Tool Choice — MCP-first hybrid (IMPORTANT)

**Never use `obsidian create content="..."` or `obsidian append content="..."` from Bash for markdown with code blocks.** zsh expands backticks and `$(...)` inside double-quoted strings — this already caused an accidental production deploy (incident 2026-04-21).

| Operation | Tool | Why |
|-----------|------|-----|
| **Write** (create, str_replace, insert) | **MCP** (`mcp__obsidian__create`, `mcp__obsidian__str_replace`, `mcp__obsidian__insert`) | Shell-safe — content passes as JSON parameter, no expansion |
| **Read** (read file, view) | **CLI** `obsidian read` | ~180 ms, indexed, safe (no content arg) |
| **Search** (duplicates, related) | **CLI** `obsidian search` | Only CLI has this — indexed, fast |
| **Orphans / backlinks / tags** | **CLI** `obsidian orphans` / `backlinks` | Only CLI has these |

Rule of thumb: **any `content=` arg with markdown → MCP**. Everything else (read, search, index queries) → CLI.

## When to Trigger

- After completing a feature / PR / fix
- After significant research session
- Manually via `/mnemo:session`
- Do NOT trigger for trivial tasks (typo fix, one-liner)

## Workflow

### Step 1: Summarize Current Session

Analyze the conversation: what was done, key decisions, commits/PRs created, findings.

Derive a **planned filename**: `{session_prefix}{YYYY-MM-DD} {short descriptive topic}`. Topic should be specific enough to disambiguate from other sessions the same day (include PR number, Linear ticket, branch name, or primary keyword).

### Step 2: Duplicate Check (two-level)

**Level 1 — exact filename:**

```bash
obsidian read file="{planned-filename}" vault="{vault}" 2>/dev/null | head -5
```

If the read returns content → note already exists. Ask user: **append**, **overwrite**, or **rename with suffix** (e.g., `... part 2`, `... continuation`).

**Level 2 — related same-day sessions (informational only):**

```bash
obsidian search query="{session_prefix}{YYYY-MM-DD}" vault="{vault}"
```

These are NOT duplicates — same day, different topics. Show the list to the user so they can:
- Decide if this session should be merged into an existing one
- Remember to cross-link related sessions via `## Связи` / `## Links`

Do not block creation on Level 2 matches — they're context, not conflicts.

### Step 3: Create Session Note (MCP — mandatory)

**Always use `mcp__obsidian__create` for creation.** Never CLI with inline `content=`.

```
mcp__obsidian__create(
  path: "{planned-filename}.md",
  file_text: """---
type: session
tags: [session, {project}, {topics}]
date: {YYYY-MM-DD}
branch: {branch-name if exists}
project: {project-name}
session_id: {CLAUDE_SESSION_ID if available}
---

# {planned-filename}

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
"""
)
```

Where `{session_prefix}` comes from `config.taxonomy.session.prefix`, `{links_section}` from `config.links_section`, and `{CLAUDE_SESSION_ID}` from the environment (empty string if not available).

**Why MCP here:** frontmatter and body may contain any markdown — code blocks with backticks, `$(...)` samples, shell snippets. MCP passes `file_text` as a JSON parameter; no shell involved.

### Step 4: Verify MOC Link

**Read MOC (CLI — safe, read-only):**

```bash
obsidian read file="{MOC name}" vault="{vault}"
```

Check if the new session note is listed.

**If missing — append link (MCP preferred):**

```
mcp__obsidian__str_replace(
  path: "{MOC name}.md",
  old_str: "{some stable anchor line near the session list}",
  new_str: "{same anchor}\n- [[{session note name}]]"
)
```

Alternatively, if the MOC has a predictable append point, use `mcp__obsidian__insert` with a line number.

**CLI fallback (only if link text has no backticks/`$()`):** `obsidian append file="{MOC}" content="- [[{name}]]"` — a plain wikilink is safe, but prefer MCP for consistency.

### Step 5: Update Session Handoff

**Read handoff (CLI — safe):**

```bash
obsidian read file="{handoff_note}" vault="{vault}"
```

**Update with MCP `str_replace` — targeted, not blind append:**

- Remove completed pending items from previous sessions
- Add new pending items from current session (if any)
- Update context carry-over section

```
mcp__obsidian__str_replace(
  path: "{handoff_note}.md",
  old_str: "{old section content}",
  new_str: "{updated section content}"
)
```

If handoff note doesn't exist, create it via `mcp__obsidian__create` (same structure as `mnemo:setup` step 7).

### Step 6: Orphan Check

```bash
obsidian orphans vault="{vault}"
```

If the newly created note appears in orphans, warn the user — it means no `## Связи` links or MOC didn't get updated.

### Step 7: Confirm

Output summary:
- Note name
- MOC updated (yes/no)
- Handoff updated (yes/no)
- Orphan status (clean / flagged)

## Rules

- **MCP for any write with markdown body** — non-negotiable, shell-safety
- **CLI for read/search/index** — faster, indexed, unique functions
- **No inline `obsidian create content="..."` with markdown** — banned
- **Two-level duplicate check** — exact-read + same-day-search
- **Include session_id in frontmatter** — disambiguates same-day sessions
- **No session notes for trivial work** — only significant sessions
- **Branch field optional** — research sessions don't have branches
- **Handoff file: targeted `str_replace`, not blind append** — pending items shouldn't accumulate infinitely
- **Links section is mandatory** — at least one MOC link
- **Ghost notes generously** — wrap projects, technologies, people in `[[wikilinks]]`

## Gotchas

- **"Unable to connect to main process"** — Obsidian IPC hung. Fix: quit Obsidian (Cmd+Q), reopen, wait 3 seconds, retry
- **Obsidian must be open** — all tools (CLI + MCP) require running app
- **MCP `create` signature**: `path` (not `name`), `file_text` (not `content`). Path is relative to vault root, include `.md` extension
- **Always check duplicate before creating** — prevents clobbering same-day work
- **`str_replace` requires exact match** — copy the anchor text verbatim from read output

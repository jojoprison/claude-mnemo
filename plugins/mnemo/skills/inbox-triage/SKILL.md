---
name: inbox-triage
description: "Use when inbox notes need classification — converts inbox captures into proper typed notes (atom, molecule, source, session). Invoke after mnemo:health shows inbox backlog, or manually."
user-invocable: false
model: haiku
---

# mnemo:sort — Classify Inbox Notes

Review unclassified inbox notes one by one and convert them to proper typed notes.

## Prerequisites

- **Obsidian must be open**

## Config

Read `vault`, `taxonomy`, and `links_section` from `~/.mnemo/config.json`.

## Workflow

### Step 1: Find Inbox Notes

```bash
obsidian search query="type: inbox" vault="{vault}"
```

If none found: "No inbox notes to classify."

### Step 2: Present Each Note

For each inbox note, read it:

```bash
obsidian read file="{note_name}" vault="{vault}"
```

Show content and suggest classification:

```
📬 Inbox note 1/4: "Inbox — HisPO for pipeline stabilization"

Content: "idea: use HisPO from LongCat for pipeline stabilization"

Suggested type: atom (single concept/fact)
Suggested name: "Atom — HisPO algorithm for MoE training stabilization"
Suggested tags: [atom, agentic-rl, moe, antomate]
Suggested MOC: [[MOC — Agent Self-Correction]]

Actions:
  [1] Accept suggestion
  [2] Change type (molecule/source/session)
  [3] Edit name/tags
  [4] Skip for now
  [5] Delete (not useful)
```

### Step 3: Apply Classification

On user confirmation:

1. Read the original inbox note content
2. Delete the inbox note: `obsidian delete file="{old_name}" vault="{vault}"`
3. Create new typed note via **MCP** (shell-safe for arbitrary markdown):
   ```
   mcp__obsidian__create(
     path: "{new_name}.md",
     file_text: """---
type: {chosen_type}
tags: [{type}, {tags}]
date: {original_date}
source: {if applicable}
---

# {new_name}

{original content, cleaned up}

## {links_section}
- [[{suggested MOC}]]
"""
   )
   ```

   **Why MCP, not CLI:** content from inbox may contain code blocks with backticks or `$(...)`. CLI `obsidian create content="..."` would trigger zsh command substitution (real incident 2026-04-21, accidental prod deploy).

4. Add to MOC — MCP for consistency, or CLI for plain wikilink appends:
   ```
   mcp__obsidian__str_replace(
     path: "{MOC}.md",
     old_str: "{stable anchor near list}",
     new_str: "{same anchor}\n- [[{new_name}]]"
   )
   ```
   CLI fallback (plain wikilink — no backticks, safe):
   `obsidian append file="{MOC}" vault="{vault}" content="- [[{new_name}]]"`

### Step 4: Summary

```
📊 Inbox triage complete

Classified: 3
  - Atom — HisPO algorithm → MOC — Agent Self-Correction
  - Source — WeChat agent trends → MOC — AI ML Tools
  - Molecule — CLI vs MCP cost analysis → MOC — Memory Systems
Skipped: 1
Deleted: 0
Remaining in inbox: 1
```

## Gotchas

- **"Unable to connect to main process"** — Obsidian IPC hung. Fix: quit Obsidian (Cmd+Q), reopen, wait 3 seconds, retry

- **One note at a time** — don't batch classify, user confirms each
- **Preserve original date** — from inbox note frontmatter, not today's date
- **Delete old inbox note** — don't leave duplicates
- **Always add to MOC** — classified notes must not be orphans
- **Suggest, don't force** — user picks final type, name, tags
- **Clean up content** — fix typos, expand abbreviations, add context if the original note was terse

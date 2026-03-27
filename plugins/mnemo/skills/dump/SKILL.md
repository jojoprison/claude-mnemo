---
name: dump
description: "Use when you need to quickly capture a thought, idea, or note without deciding its type. Creates an inbox note for later classification. Zero friction brain dump."
user-invocable: true
model: opus
---

# mnemo:dump — Quick Capture Brain Dump

Capture a thought instantly. No classification needed. Classify later with mnemo:sort.

## Prerequisites

- **Obsidian must be open**

## Config

Read `vault` and `taxonomy.inbox` from `~/.mnemo/config.json`. If missing, run `/mn:setup` or ask user.

## Workflow

### Step 1: Accept Input

Input as argument: `/mn:dump "idea: use HisPO for pipeline stabilization"`

If no argument, ask: "What do you want to capture?"

### Step 2: Check for Duplicates

```bash
obsidian search query="{key words from input}" vault="{vault}"
```

If similar note exists — show it and ask: "Similar note found. Create new or append to existing?"

### Step 3: Generate Short Title

Extract a concise descriptive title from the input (5-8 words max).

### Step 4: Extract Auto-Tags

Scan input for recognizable entities (technology names, project names, people). Add as tags alongside `inbox` and `unclassified`. Maximum 2 extra tags.

### Step 5: Create Inbox Note

```bash
obsidian create name="{inbox_prefix}{short title}" vault="{vault}" content="---
type: inbox
tags: [inbox, unclassified, {auto_tag_1}, {auto_tag_2}]
date: {YYYY-MM-DD}
---

# {inbox_prefix}{short title}

{original input text}
"
```

Where `{inbox_prefix}` comes from `config.taxonomy.inbox.prefix` (default: `Inbox — `).

### Step 6: Confirm

Output: `📬 Saved: "{title}". Classify later with /mn:sort.`

## Gotchas

- **"Unable to connect to main process"** — Obsidian IPC hung. Fix: quit Obsidian (Cmd+Q), reopen, wait 3 seconds, retry

- **No links section** — inbox is the ONLY type exempt from this rule
- **No classification** — the whole point is zero friction. Don't try to guess atom/molecule/source
- **Still check for duplicates** — `obsidian search` before create, always
- **Minimal frontmatter** — just type, tags, date. Nothing else
- **Short titles** — "Inbox — HisPO for pipeline stabilization", NOT "Inbox — idea about using HisPO algorithm from LongCat for stabilizing our pipeline in the antomate project"
- **Auto-tags are bonus** — max 2, only obvious ones. Don't overthink

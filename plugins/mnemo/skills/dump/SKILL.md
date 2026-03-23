---
name: dump
description: "Use when you need to quickly capture a thought, idea, or note without deciding its type. Creates an inbox note for later classification. Zero friction brain dump."
user-invocable: true
model: opus
---

# mnemo:dump — Quick Capture Brain Dump

Capture a thought instantly. No classification needed. Classify later with mnemo:health reminders.

## Prerequisites

- **Obsidian must be open**

## Config

Read vault name from `config.json`. If missing, ask user.

## Workflow

### Step 1: Accept Input

Input comes as argument: `/mnemo:dump "идея: использовать HisPO для стабилизации pipeline"`

If no argument, ask: "What do you want to capture?"

### Step 2: Check for Duplicates

```bash
obsidian search query="{key words from input}" vault="{vault}"
```

If similar note exists — show it and ask: "Similar note found. Create new or append to existing?"

### Step 3: Generate Short Title

Extract a concise descriptive title from the input (5-8 words max).

### Step 4: Create Inbox Note

```bash
obsidian create name="Inbox — {short title}" vault="{vault}" content="---
type: inbox
tags: [inbox, unclassified]
date: {YYYY-MM-DD}
---

# Inbox — {short title}

{original input text}
"
```

### Step 5: Confirm

Output: `📬 Saved: "Inbox — {title}". Classify later with /mnemo:health.`

## Gotchas

- **No `## Связи` section** — inbox is the ONLY type exempt from this rule
- **No classification** — the whole point is zero friction. Don't try to guess atom/molecule/source
- **Still check for duplicates** — `obsidian search` before create, always
- **No frontmatter beyond minimum** — just type, tags, date. Nothing else
- **Short titles** — "Inbox — HisPO для pipeline стабилизации", NOT "Inbox — идея о том что можно использовать HisPO алгоритм из LongCat для стабилизации нашего pipeline в antomate проекте"

---
name: vault-search
description: "Use when searching for information across the Obsidian vault — 'what did we decide about X', 'find everything about Y', 'summarize what we know about Z'. Synthesizes answers from multiple notes with source citations."
user-invocable: false
model: sonnet
---

# mnemo:ask — Vault Knowledge Search & Synthesis

Search across the entire vault, read relevant notes, and synthesize an answer with source citations.

## Prerequisites

- **Obsidian must be open** — CLI works through app indexes

## Config

Read `vault` and `links_section` from `config.json` in the plugin config directory (`~/.mnemo/config.json`). If missing, ask user and save.

## Workflow

### Step 1: Accept Query

Input as argument: `/mnemo:ask "what did we decide about pricing strategy?"`

If no argument, ask: "What would you like to find in your vault?"

### Step 2: Extract Search Terms

Break query into 2-4 key search terms. Example:
- "what did we decide about pricing strategy?" → ["pricing", "strategy", "decision"]

### Step 3: Search Vault (parallel)

**Run all searches in parallel — single assistant message with multiple Bash tool uses.** For 4 terms this takes ~180ms total instead of ~720ms sequential.

```bash
obsidian search query="{term1}" vault="{vault}"
obsidian search query="{term2}" vault="{vault}"
obsidian search query="{term3}" vault="{vault}"
obsidian search query="{term4}" vault="{vault}"
```

Collect all unique matching notes. Deduplicate.

### Step 4: Read Top Results (parallel)

Read the most relevant notes (max 7) **in parallel — single message with multiple Bash tool uses.** ~185ms vs ~1.3s sequential for 7 notes.

```bash
obsidian read file="{note_name_1}" vault="{vault}"
obsidian read file="{note_name_2}" vault="{vault}"
...
```

### Step 5: Synthesize Answer

Compose a clear answer from the found notes. For each claim, cite the source note:

```
Based on your vault:

The pricing strategy was decided on 2026-03-14 during the pipeline review session.
Key points:
- Freemium model with usage-based tiers [Source: Session — 2026-03-14 pipeline vision]
- Enterprise plan at $99/mo was rejected as too low [Source: Atom — pricing research]
- Final decision: $29 starter, $99 pro, custom enterprise [Source: Molecule — pricing decision]

📚 Sources (3 notes):
1. [[Session — 2026-03-14 pipeline vision]]
2. [[Atom — pricing research]]
3. [[Molecule — pricing decision]]
```

### Step 6: Offer Follow-up

Ask: "Want me to search deeper, or connect any of these notes?"

## Gotchas

- **"Unable to connect to main process"** — Obsidian IPC hung. Fix: quit Obsidian (Cmd+Q), reopen, wait 3 seconds, retry

- **CLI for search, not MCP** — obsidian CLI search is 70,000x cheaper
- **Max 7 notes read** — don't blow context reading the entire vault
- **Always cite sources** — every claim must reference a specific note
- **If nothing found** — say so honestly, suggest alternative search terms
- **Don't hallucinate** — only answer from what's in the vault, not from general knowledge
- **Respect note types** — Sessions contain decisions, Atoms contain facts, Molecules contain insights

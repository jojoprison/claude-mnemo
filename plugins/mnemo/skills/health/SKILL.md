---
name: health
description: "Use when checking Obsidian vault health, finding orphans, broken links, or getting vault statistics. Invoke weekly, after mass note creation, or when asked about vault state."
user-invocable: true
context: fork
model: opus
---

# mnemo:health — Vault Health Check & Analytics

Run a comprehensive health check on the Obsidian vault: orphans, broken links, missing sections, stale notes, and growth statistics.

## Prerequisites

- **Obsidian must be open** — CLI works through app indexes
- **Obsidian CLI installed** — `obsidian` command available in PATH

## Config

Read vault name from `config.json` in this skill's directory. If missing, ask the user and save:

```json
{
  "vault": "main"
}
```

## Workflow

### Step 1: Orphan Detection

```bash
obsidian orphans vault="{vault}"
```

List notes with zero backlinks. These are invisible in Graph View.

### Step 2: Unresolved Links (Ghost Notes)

```bash
obsidian unresolved vault="{vault}"
```

Show `[[wikilinks]]` that point to non-existent files. Ghost notes are NORMAL (entity discovery) — only flag if count seems excessive (>200).

### Step 3: Tag Distribution

```bash
obsidian tags counts sort=count vault="{vault}"
```

Show top tags. Flag tags used only once (potential typos).

### Step 4: Notes by Type

Count notes by `type:` frontmatter field. Expected types from config taxonomy:

- `atom` — single facts
- `molecule` — synthesized insights
- `source` — external sources
- `session` — work session summaries
- `moc` — Maps of Content
- `inbox` — unclassified captures (from mnemo:dump)

Use `obsidian search` or `obsidian files` + read frontmatter.

### Step 5: Missing `## Связи` Section

Find notes that do NOT contain `## Связи` heading. These are disconnected from the knowledge graph. Inbox notes are exempt.

### Step 6: Inbox Backlog

Count notes with `type: inbox`. Remind user to classify them.

### Step 7: Stale Notes

Find notes older than 30 days with zero backlinks (not orphans from Step 1 — those have zero outgoing links, stale = zero incoming).

### Step 8: Output Report

Format as:

```
📊 Vault Health Report ({date})

Total: {N} notes
  Atoms: {N} | Molecules: {N} | Sources: {N}
  Sessions: {N} | MOCs: {N} | Inbox: {N} | Other: {N}

🔴 Orphans: {N}
  - Note Name 1
  - Note Name 2

🟡 Missing ## Связи: {N}
  - Note Name 1

📬 Inbox backlog: {N} notes waiting for classification

🔗 Unresolved wikilinks: {N}
📏 Tags: {N} total, {N} used once

🏆 Top-5 Hubs (most backlinks):
  1. MOC — Security (34)
  2. MOC — AI ML Tools (28)
  ...

💤 Stale (30d+ no backlinks): {N}
```

## Gotchas

- Obsidian must be open — CLI communicates through the running app
- `obsidian orphans` may return empty on small vaults — this is OK, not an error
- Reference notes like `Obsidian Note Taxonomy` are NOT orphans even if few backlinks
- Ghost notes (unresolved wikilinks) are a FEATURE, not a bug — they enable entity discovery
- Use CLI for everything, MCP only for str_replace/insert (70,000x cheaper)
- Do NOT auto-fix anything — only report. User decides what to fix

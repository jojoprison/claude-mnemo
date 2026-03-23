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

Read from `~/.mnemo/config.json`. If missing, run `/mnemo:setup` or ask user for vault name and save.

Required fields: `vault`, `taxonomy`, `links_section`.

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

Show `[[wikilinks]]` pointing to non-existent files. Ghost notes are NORMAL (entity discovery) — only flag if count seems excessive (>200).

### Step 3: Tag Distribution

```bash
obsidian tags counts sort=count vault="{vault}"
```

Show top 15 tags. Flag tags used only once (potential typos).

### Step 4: Notes by Type

For each type in `config.taxonomy`, count notes:

```bash
obsidian search query="type: atom" vault="{vault}"
obsidian search query="type: molecule" vault="{vault}"
obsidian search query="type: source" vault="{vault}"
obsidian search query="type: session" vault="{vault}"
obsidian search query="type: moc" vault="{vault}"
obsidian search query="type: inbox" vault="{vault}"
```

Count results for each. Total = sum of all + uncategorized.

### Step 5: Missing Links Section

Search for notes that do NOT contain the configured `links_section` heading. Approach:

1. Get all markdown files: `obsidian files ext=md vault="{vault}"`
2. For each note with a known type prefix (Atom, Molecule, Source, Session, MOC):
   - `obsidian read file="{name}" vault="{vault}"`
   - Check if `{links_section}` heading exists in content
3. Inbox notes are **exempt** from this check.

Report notes missing the section.

### Step 6: Inbox Backlog

Count from Step 4's inbox search. If > 0, remind:
"N inbox notes waiting for classification. Run /mnemo:sort to classify."

### Step 7: Stale Notes

Find notes with `date:` in frontmatter older than 30 days, then check backlinks:

```bash
obsidian backlinks file="{note_name}" vault="{vault}"
```

If zero backlinks AND date > 30 days ago → stale.

### Step 8: Top Hubs

For each MOC, count backlinks:

```bash
obsidian backlinks file="{moc_name}" vault="{vault}"
```

Sort by count, show top 5.

### Step 9: Output Report

```
📊 Vault Health Report ({date})

Total: {N} notes
  Atoms: {N} | Molecules: {N} | Sources: {N}
  Sessions: {N} | MOCs: {N} | Inbox: {N} | Other: {N}

🔴 Orphans: {N}
  - Note Name 1
  - Note Name 2

🟡 Missing {links_section}: {N}
  - Note Name 1

📬 Inbox backlog: {N} notes — run /mnemo:sort to classify

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
- Reference notes (taxonomy docs, templates) are NOT orphans even if few backlinks
- Ghost notes (unresolved wikilinks) are a FEATURE, not a bug — they enable entity discovery
- Use CLI for everything, MCP only for str_replace/insert (70,000x cheaper)
- Do NOT auto-fix anything — only report. User decides what to fix
- Step 5 is the most expensive step (reads many files) — skip if vault > 500 notes and user didn't specifically ask for it

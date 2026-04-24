---
name: vault-health
description: "Use when checking Obsidian vault health, finding orphans, broken links, or getting vault statistics. Invoke weekly, after mass note creation, or when asked about vault state."
user-invocable: false
model: haiku
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

**Steps 1-4 run in parallel** — single assistant message with 4 Bash tool uses. These are independent CLI queries against the same indexed vault, ~180ms each → 180ms total vs 720ms sequential.

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

Use tags (indexed, reliable) instead of fulltext search:

```bash
obsidian tags counts sort=count vault="{vault}"
```

From the output, extract counts for taxonomy tags: `#atom`, `#molecule`, `#source`, `#session`, `#moc`, `#inbox`. These correspond to `config.taxonomy.*.tag` values.

Total notes count:

```bash
obsidian files ext=md vault="{vault}" total
```

### Step 5: Missing Links Section (batched grep — 1800x faster)

**Do NOT loop `obsidian read` per file** — on a 1000-note vault that's ~180s (1000 × 180ms). Use a single filesystem-level grep against the vault directory. Get vault path from `obsidian vault vault="{name}"` (tab-separated, path is column 2 of the `path` line).

```bash
# One call to get vault filesystem path
VAULT_PATH=$(obsidian vault vault="{vault}" | awk '/^path\s/{print $2}')

# Single recursive grep -L lists files NOT containing the links section heading.
# Filter to taxonomy-prefixed notes, exclude inbox.
grep -rL --include="*.md" "{links_section}" "$VAULT_PATH" 2>/dev/null \
  | grep -E "(Atom|Molecule|Source|Session|MOC) — " \
  | grep -v "Inbox —"
```

**Measured on 999-note vault: ~49ms vs ~180s serial** — 3600x speedup. Safe to run always, no need to skip on large vaults.

Inbox notes are **exempt** via the `grep -v "Inbox —"` filter.

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
- Step 5 now uses filesystem grep, safe on any vault size (1800x faster than per-file reads)

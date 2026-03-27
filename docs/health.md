# mnemo:health — Vault Health Check & Analytics

## Overview

Comprehensive audit of your Obsidian vault: orphans, broken links, missing sections, stale notes, type distribution, and hub analysis.

## Usage

```
/mn:health
```

No arguments needed. Reads vault name from `~/.mnemo/config.json`.

## What It Checks

| Check | What it finds | Severity |
|-------|--------------|----------|
| Orphans | Notes with zero backlinks (invisible in Graph View) | 🔴 High |
| Missing links section | Notes without `## Links` / `## Связи` (disconnected from graph) | 🟡 Medium |
| Inbox backlog | Unclassified inbox notes from `/mn:dump` | 📬 Info |
| Unresolved wikilinks | `[[Ghost Notes]]` pointing to non-existent files | ℹ️ Normal |
| Tag typos | Tags used only once (potential misspelling) | 🟡 Medium |
| Stale notes | 30+ days old with zero backlinks | 💤 Low |

## Example Output

```
📊 Vault Health Report (2026-03-24)

Total: 375 notes
  Atoms: 221 | Sessions: 96 | Sources: 21
  Molecules: 19 | MOCs: 17 | Inbox: 0

🔴 Orphans: 14
  - Atom — old note without links
  - Session — 2026-03-14 forgotten session

🟡 Missing ## Связи: 2
  - Atom — quick note without links section

📬 Inbox backlog: 0

🏆 Top-5 Hubs (most backlinks):
  1. MOC — Arcadia (102)
  2. MOC — Claude Code Tools (54)
  3. MOC — Infrastructure (37)
```

## Important Notes

- **Ghost notes are a feature** — `[[Technology]]` links to non-existent files are intentional for entity discovery in Graph View
- **Non-destructive** — only reports, never auto-fixes. You decide what to fix
- **Inbox notes are exempt** from the missing links section check
- Run weekly or after creating many notes at once

## Related Skills

- `/mn:connect` — fix orphans by discovering hidden connections
- `/mn:sort` — classify inbox backlog

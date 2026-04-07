# mnemo:sort — Classify Inbox Notes

## Overview

Reviews unclassified inbox notes one by one and converts them to proper typed notes (atom, molecule, source, session).

## Usage

```
/mn:sort
```

No arguments. Finds all `type: inbox` notes automatically.

## How It Works

1. Searches for all notes with `type: inbox`
2. Shows each note with a classification suggestion
3. You pick: accept, change type, edit, skip, or delete
4. Renames the note, updates frontmatter, adds links section, links to MOC
5. Repeats until inbox is empty

## Example Interaction

```
📬 Inbox note 1/4: "Inbox — HisPO for pipeline stabilization"

Content: "idea: use HisPO for pipeline stabilization"

Suggested type: atom
Suggested name: "Atom — HisPO algorithm for MoE training stabilization"
Suggested tags: [atom, agentic-rl, moe, antomate]
Suggested MOC: [[MOC — Agent Self-Correction]]

Actions:
  [1] Accept suggestion
  [2] Change type (molecule/source/session)
  [3] Edit name/tags
  [4] Skip for now
  [5] Delete
```

## Important Notes

- **One note at a time** — user confirms each classification
- **Preserves original date** — from inbox note, not today
- **Deletes old inbox note** — no duplicates left behind
- **Always adds to MOC** — classified notes won't be orphans
- **Cleans up content** — fixes typos, expands abbreviations

## Related Skills

- `/mn:save` — creating inbox notes (routes quick thoughts to inbox)
- `/mn:health` — shows inbox backlog count

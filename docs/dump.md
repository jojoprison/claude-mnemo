# mnemo:dump — Quick Capture Brain Dump

## Overview

Capture a thought in 2 seconds. No classification, no tags, no structure. Just dump it and classify later.

## Usage

```
/mn:dump "idea: use HisPO for pipeline stabilization"
/mn:dump "remember to check orphans after this session"
/mn:dump "interesting pattern: WeChat agent bridge = same as Telegram channels"
```

## How It Works

1. Takes your text as input
2. Checks for duplicate notes
3. Generates a short title (5-8 words)
4. Creates an `Inbox — {title}` note with minimal frontmatter
5. Done. Classify later with `/mn:sort`

## Example Output

```
📬 Saved: "Inbox — HisPO for pipeline stabilization"
   Classify later with /mn:sort
```

## What Gets Created

```markdown
---
type: inbox
tags: [inbox, unclassified, agentic-rl]
date: 2026-03-24
---

# Inbox — HisPO for pipeline stabilization

idea: use HisPO for pipeline stabilization
```

## Important Notes

- **No `## Links` section** — inbox is the only type exempt
- **No classification** — the whole point is zero friction
- **Auto-tags** — extracts max 2 obvious tags from content (technology names, project names)
- **Duplicate check** — still searches before creating

## Related Skills

- `/mn:sort` — classify inbox notes later
- `/mn:health` — reminds you about inbox backlog

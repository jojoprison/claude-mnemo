# mnemo:check-gmail — Gmail to Obsidian Bridge

## Overview

Scans your Gmail inbox, saves important emails as Obsidian notes, and flags deadlines in your daily note.

## Usage

```
/mnemo:check-gmail
```

No arguments. Scans last 10 unread emails.

## Prerequisites

- **gws CLI** installed and authorized (`gws gmail auth`)
- **gmail_enabled: true** in `~/.mnemo/config.json`
- **Obsidian** must be running

## How It Works

1. Fetches unread emails via `gws gmail list --unread --max 10`
2. Classifies each: important (from people, tasks, deadlines) vs skip (newsletters, notifications)
3. Saves important emails as `Inbox — Email: {subject}` notes
4. Flags deadlines in daily note via `obsidian daily:append`
5. **NEVER marks emails as read**

## Example Output

```
📬 Email check complete

Scanned: 10 unread
Saved: 2 important
Skipped: 8 (newsletters/notifications)

Saved:
1. "Inbox — Email: Q3 budget review" — from marco@company.com
2. "Inbox — Email: Deploy approval needed" — from ops@company.com

Deadlines found: 1 (added to daily note)
```

## What Gets Created

```markdown
---
type: inbox
tags: [inbox, email, company-com]
date: 2026-03-24
source: "Gmail from marco@company.com"
---

# Inbox — Email: Q3 budget review

**From:** marco@company.com
**Date:** 2026-03-24
**Subject:** Q3 budget review

## Content
Marco wants the budget report by Friday. Key numbers: ...

## Action Items
- [ ] Prepare Q3 budget report

## Deadlines
- Friday 2026-03-28: Q3 budget report due
```

## Important Notes

- **NEVER marks as read** — iron rule, `gmail_mark_read: false` in config
- **Summarizes, doesn't copy** — email body is summarized for privacy and tokens
- **Selective** — only saves truly important emails, skips noise
- **Inbox type** — classify later with `/mnemo:sort`

## Related Skills

- `/mnemo:sort` — classify saved email notes
- `/mnemo:health` — shows email inbox backlog

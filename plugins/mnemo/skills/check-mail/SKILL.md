---
name: check-mail
description: "Use when checking email and saving important messages to Obsidian vault. Uses gws CLI for Gmail. NEVER marks emails as read without explicit user request."
user-invocable: true
context: fork
model: opus
---

# mnemo:check-mail — Gmail to Obsidian Bridge

Scan Gmail inbox, save important emails as Obsidian notes, flag deadlines.

## Prerequisites

- **Obsidian must be open**
- **gws CLI installed and authorized** — `gws gmail list` must work

## Config

Read from `config.json`:

```json
{
  "vault": "main",
  "gmail_mark_read": false
}
```

`gmail_mark_read` MUST be `false` by default. Only change if user explicitly requests.

## Workflow

### Step 1: Fetch Unread Emails

```bash
gws gmail list --unread --max 10
```

### Step 2: Classify Importance

For each email, classify:
- **Important** — from real people, contains tasks/deadlines/decisions, project-related
- **Skip** — newsletters, notifications, automated alerts, marketing

### Step 3: Save Important Emails

For each important email:

```bash
obsidian create name="Inbox — Email: {subject short}" vault="{vault}" content="---
type: inbox
tags: [inbox, email, {sender-domain}]
date: {YYYY-MM-DD}
source: \"Gmail from {sender}\"
---

# Inbox — Email: {subject}

**From:** {sender}
**Date:** {email date}
**Subject:** {full subject}

## Content
{email body summary — NOT full text, summarize key points}

## Action Items
- [ ] {extracted action items if any}

## Deadlines
- {extracted deadlines if any}
"
```

### Step 4: Flag Deadlines in Daily Note

If any email contains a deadline:

```bash
obsidian daily:append vault="{vault}" content="⏰ Deadline from email: {subject} — {deadline date}"
```

### Step 5: Summary

Output:

```
📬 Email check complete

Scanned: {N} unread
Saved: {N} important
Skipped: {N} (newsletters/notifications)

Saved:
1. "Inbox — Email: {subject}" — from {sender}
2. ...

Deadlines found: {N}
```

### Step 6: DO NOT Mark as Read

**CRITICAL: NEVER mark emails as read.** This is a hard rule. Even if user says "mark as read" — confirm twice before doing it.

## Gotchas

- **NEVER mark as read** — iron rule, no exceptions without double confirmation
- **gws CLI must be authorized** — if `gws gmail list` fails, tell user to run `gws gmail auth`
- **Summarize, don't copy** — email body goes as summary, not raw paste (privacy + tokens)
- **Not every email is worth saving** — be selective, only truly important ones
- **Inbox type** — saved emails are `type: inbox`, classify later with mnemo:health
- **No ## Связи for inbox notes** — standard inbox exemption

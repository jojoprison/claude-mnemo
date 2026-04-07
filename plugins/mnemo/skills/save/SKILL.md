---
name: save
description: "Use when user says 'remember this', 'save to memory', 'запомни', 'в память', 'сохрани', or when significant facts, decisions, or findings need to be persisted. Routes to multiple storage backends with graceful degradation."
user-invocable: true
context: fork
model: opus
---

# mnemo:save — Memory Routing Cascade

Save information to multiple memory backends with graceful degradation. Each backend is tried independently — if one fails, others still work.

## Prerequisites

- **Obsidian should be open** — but skill works even if it's not (skips Obsidian, uses other backends)

## Config

Read from `~/.mnemo/config.json`:

```json
{
  "vault": "main",
  "cascade": {
    "obsidian": { "enabled": true },
    "claude_mem": { "enabled": true, "url": "http://127.0.0.1:37777" },
    "memory_dir": { "enabled": true },
    "claude_md": { "enabled": false }
  }
}
```

If `cascade` section is missing, defaults: obsidian=true, claude_mem=true, memory_dir=true, claude_md=false.

## Workflow

### Step 0: Classify the Input

Determine what type of information is being saved:

| Type | Goes to | Example |
|------|---------|---------|
| **fact** | Obsidian Atom + claude-mem | "Heroku standard-0 has 25 auto-backups" |
| **insight** | Obsidian Molecule + claude-mem | "CLI-first is 70,000x cheaper because of token savings" |
| **decision** | Obsidian Atom + claude-mem + memory/ | "We chose SCOPE over TextGrad for self-correction" |
| **gotcha** | Obsidian Atom + memory/ + possibly CLAUDE.md | "execSync with shell=true is banned in antomate" |
| **source** | Obsidian Source + claude-mem | External article, tool, research finding |
| **rule** | CLAUDE.md (if error-preventing) + memory/ | "Never mark Gmail as read without explicit request" |
| **quick thought** | Create Obsidian inbox note | Unstructured ideas |

### Step 1: Obsidian (Primary — for the user)

**Skip if:** `cascade.obsidian.enabled` is false, or Obsidian CLI returns "Unable to connect"

```bash
obsidian search query="{key words}" vault="{vault}"
```

If duplicate found → ask: update existing or create new?

Create appropriate note based on classification:

```bash
# For facts/decisions/gotchas:
obsidian create name="{type_prefix}{descriptive title}" vault="{vault}" content="---
type: {type}
tags: [{type}, {topic_tags}]
date: {YYYY-MM-DD}
source: \"{where this came from}\"
---

# {type_prefix}{title}

{content}

{links_section}
- [[{relevant MOC}]]
- [[{ghost notes for entities}]]
"
```

Then add to relevant MOC:

```bash
obsidian append file="{MOC}" vault="{vault}" content="- [[{note name}]]"
```

**On error:** Log `⚠️ Obsidian: skipped (not connected)`, continue to next backend.

### Step 2: claude-mem (Semantic Search — cross-session recall)

**Skip if:** `cascade.claude_mem.enabled` is false

```bash
curl -s -X POST http://{claude_mem_url}/api/memory/save \
  -H "Content-Type: application/json" \
  -d '{
    "content": "{one-line summary of what was saved}",
    "metadata": {
      "type": "{type}",
      "project": "{current project or 'general'}",
      "obsidian_note": "{note name if created}"
    }
  }'
```

**On error:** Log `⚠️ claude-mem: skipped (port {port} not responding)`, continue.

### Step 3: memory/ (For Claude — error prevention)

**Skip if:** `cascade.memory_dir.enabled` is false

Only write here if the information **prevents Claude from making errors** in future sessions:
- Gotchas, commands, conventions
- NOT business context (that's Obsidian's job)

**Path resolution (CRITICAL):**
The "memory/" directory is Claude Code's **auto-memory** directory, NOT `./memory/` in the project root.

To find the correct path, look for the `MEMORY.md` file that is already loaded in your conversation context. Its path follows the pattern:
```
~/.claude/projects/-{slugified-cwd}/memory/
```
For example: `~/.claude/projects/-Users-jkaseq-Documents-projects-bts-holding/memory/`

**NEVER create or write to `./memory/` in the project root** — that would put memory files in the git repo.

Write or append to relevant topic file in that directory. Use `~/.claude/memory/` only for cross-project info.

**On error:** Log `⚠️ memory/: skipped (directory not found)`, continue.

### Step 4: CLAUDE.md (Only critical error-preventing rules)

**Skip if:** `cascade.claude_md.enabled` is false (default)

Only write here if the rule is:
- 1-2 lines max
- Violation would cause a real error or bad behavior
- Not already covered by Obsidian or memory/

This is almost never needed. Most things go to Obsidian + claude-mem.

### Step 5: Report

```
💾 Memory saved:

Content: "{short summary}"
Type: {atom/molecule/source/decision/gotcha}

Backends:
  1. Obsidian  ✅ → "Atom — {title}" in MOC — {name}
  2. claude-mem ✅ → semantic search indexed
  3. memory/   ⏭  skipped (not error-preventing)
  4. CLAUDE.md ⏭  skipped (not critical rule)
```

Or with failures:

```
💾 Memory saved (partial):

  1. Obsidian  ⚠️ skipped (not connected — restart Obsidian)
  2. claude-mem ✅ → indexed
  3. memory/   ✅ → ~/.claude/memory/topic.md updated

⚠️ Run /mnemo:save again after restarting Obsidian to complete sync.
```

## Decision Matrix

| Information type | Obsidian | claude-mem | memory/ | CLAUDE.md |
|-----------------|----------|-----------|---------|-----------|
| Fact (atomic) | ✅ Atom | ✅ | ❌ | ❌ |
| Insight (synthesized) | ✅ Molecule | ✅ | ❌ | ❌ |
| External source | ✅ Source | ✅ | ❌ | ❌ |
| Decision | ✅ Atom | ✅ | ✅ if prevents errors | ❌ |
| Gotcha | ✅ Atom | ✅ | ✅ | ✅ if critical |
| Command/convention | ✅ Atom | ✅ | ✅ | ❌ |
| Error-preventing rule | ❌ | ❌ | ✅ | ✅ |
| Quick unstructured thought | ✅ Inbox | ❌ | ❌ | ❌ |

## Gotchas

- **"Unable to connect to main process"** — Obsidian IPC hung. Fix: quit Obsidian (Cmd+Q), reopen, wait 3 seconds, retry
- **Graceful degradation is the point** — never fail completely, always save to at least one backend
- **Don't duplicate Obsidian content in memory/** — Obsidian = user's memory, memory/ = Claude's memory. Different audiences
- **claude-mem is optional** — many users won't have it. Skip silently
- **CLAUDE.md is almost never written to** — only 1-2 line rules that prevent actual errors. Target: <120 lines total
- **CLI first for Obsidian** — never use MCP for search/create (70,000x cheaper)
- **memory/ path is NOT `./memory/`** — it's `~/.claude/projects/-{slug}/memory/`. Writing to project root creates files in git. Find the correct path from MEMORY.md in context
- **Always check duplicates** before creating Obsidian notes
- **Ghost notes generously** — wrap entities in `[[wikilinks]]`
- **MOC link mandatory** for Obsidian notes (except inbox)

---
name: memory-routing
description: "Use whenever the user says 'remember this', 'save to memory', 'запомни', 'в память', 'сохрани', 'в мнемо', solved a bug worth remembering, made a non-obvious decision, or learned a gotcha. Routes each item to the right combination of Obsidian + claude-mem + memory/ + CLAUDE.md with graceful degradation if a backend is unavailable."
user-invocable: false
model: inherit
---

# mnemo:save — Memory Routing Cascade

Save information to multiple memory backends with graceful degradation. Each backend is tried independently — if one fails, others still work.

## Prerequisites & config

Obsidian is preferred but not required (skill degrades gracefully). Config at `~/.mnemo/config.json` — full schema including `cascade.*` toggles in `references/config-schema.md`.

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

**Create note — MCP (shell-safe for markdown with code blocks):**

```
mcp__obsidian__create(
  path: "{type_prefix}{descriptive title}.md",
  file_text: """---
type: {type}
tags: [{type}, {topic_tags}]
date: {YYYY-MM-DD}
source: "{where this came from}"
---

# {type_prefix}{title}

{content}

{links_section}
- [[{relevant MOC}]]
- [[{ghost notes for entities}]]
"""
)
```

**Why MCP:** content may contain code blocks with backticks or `$(...)` — CLI `obsidian create content="..."` would trigger zsh command substitution. See `references/tool-routing.md` for the full rule.

**Add to MOC — MCP `str_replace` for targeted insert, or CLI for plain wikilinks:**

```
mcp__obsidian__str_replace(
  path: "{MOC}.md",
  old_str: "{stable anchor line near list}",
  new_str: "{same anchor}\n- [[{note name}]]"
)
```

CLI fallback for plain wikilink appends (safe — no backticks):

```bash
obsidian append file="{MOC}" vault="{vault}" content="- [[{note name}]]"
```

**On error:** Log `⚠️ Obsidian: skipped (not connected)`, continue to next backend.

### Step 2: claude-mem (Semantic Search — cross-session recall)

**Skip if:** `cascade.claude_mem.enabled` is false

Auto-detect the installed claude-mem version so observations carry provenance (useful when filtering pre-v12 data from post-v12 data):

```bash
CM_VERSION=$(ls -1 ~/.claude/plugins/cache/thedotmack/claude-mem/ 2>/dev/null | sort -V | tail -1)

curl -s -X POST http://{claude_mem_url}/api/memory/save \
  -H "Content-Type: application/json" \
  -d "{
    \"content\": \"{one-line summary of what was saved}\",
    \"metadata\": {
      \"type\": \"{type}\",
      \"project\": \"{current project or 'general'}\",
      \"obsidian_note\": \"{note name if created}\",
      \"obsidian_vault\": \"{vault}\",
      \"claude_mem_version\": \"${CM_VERSION:-unknown}\"
    }
  }"
```

**Why `obsidian_note` + `obsidian_vault`:** lets `claude-mem search` results link back to the full Obsidian note. Future `/mn:ask --deep` can show the user a direct wikilink alongside the observation.

**Why `claude_mem_version`:** v11.0.1 disabled semantic-inject by default, v12.0.0 introduced the file-read gate. Tagging observations by version lets retrieval logic filter legacy entries when needed.

**On error:** Log `⚠️ claude-mem: skipped (port {port} not responding)`, continue.

### Step 3: memory/ (For Claude — error prevention)

**Skip if:** `cascade.memory_dir.enabled` is false

Only write here if the information **prevents Claude from making errors** in future sessions:
- Gotchas, commands, conventions
- NOT business context (that's Obsidian's job)

**Path resolution:** memory/ is Claude Code's auto-memory directory at `~/.claude/projects/-{slugified-cwd}/memory/`, **not** `./memory/` in the project root. Find the correct path by reading the `MEMORY.md` already loaded in your conversation context — its path shows the right slug. Use `~/.claude/memory/` only for cross-project info. See `references/gotchas.md` for why this matters.

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

Common failures in `references/gotchas.md`. Tool-routing rationale in `references/tool-routing.md`. Skill-specific rules:

- **Graceful degradation is the point** — never fail completely. If Obsidian IPC is hung, skip it and save to claude-mem + memory/. The user can retry when Obsidian recovers.
- **Don't duplicate Obsidian content in memory/** — different audiences. Obsidian is for the user (cite-able, searchable in vault); memory/ is for Claude (error prevention across sessions).
- **claude-mem is optional** — many users won't have it running on :37777. Skip silently, don't warn.
- **CLAUDE.md is almost never written to** — only 1-2 line rules that prevent actual errors. Target: <120 lines total to preserve prompt budget.
- **Always check duplicates** before creating Obsidian notes — clobbering a note silently is worse than any write latency.
- **Ghost notes generously** — wrap entities in `[[wikilinks]]` even when the target doesn't exist yet. Enables future entity discovery.
- **MOC link mandatory** for typed Obsidian notes (Atom/Molecule/Source/Session). Inbox notes are exempt.

---
name: link-discovery
description: "Use after creating a new Obsidian note to discover hidden connections with existing notes. Shows suggestions, does NOT auto-apply. Invoke with note name as argument."
user-invocable: false
context: fork
model: opus
---

# mnemo:connect — Discover Hidden Links

Analyze a note and discover connections to other notes in the vault that aren't linked yet.

## Prerequisites

- **Obsidian must be open** — CLI works through app indexes

## Config

Read `vault` and `links_section` from `~/.mnemo/config.json`. If missing, run `/mnemo:setup` or ask user.

## Workflow

### Step 1: Identify Target Note

Accept note name as argument: `/mnemo:connect "Atom — LongCat-Flash-Prover"`

If no argument, ask: "Which note should I analyze for connections?"

### Step 2: Read the Note

```bash
obsidian read file="{note_name}" vault="{vault}"
```

Extract:
- Key concepts, technologies, names mentioned in text
- Existing `[[wikilinks]]`
- Existing links in `{links_section}` section

### Step 3: Search for Related Notes

For each key concept (max 7):

```bash
obsidian search query="{concept}" vault="{vault}"
```

Collect all matching notes. Exclude the target note itself.

### Step 4: Check Existing Backlinks

```bash
obsidian backlinks file="{note_name}" vault="{vault}"
```

These are already connected — exclude from suggestions.

### Step 5: Generate Suggestions

Compare: notes found by search MINUS notes already linked (wikilinks + backlinks).

For each suggestion, explain WHY it's relevant (shared concept, shared tag, complementary topics).

### Step 6: Present (DO NOT auto-apply)

```
🔗 Connection suggestions for "{note_name}"

Already connected: {N} notes
New suggestions: {N}

1. [[Atom — SCOPE beats TextGrad]]
   Why: Both discuss agentic RL stability — HisPO and SCOPE solve similar problems

2. [[MOC — Agent Self-Correction]]
   Why: Note mentions trial→verify→reflect cycle, this MOC covers the same pattern
   Action: Add to MOC? (currently not listed there)

3. [[Session — ANT-14 TextGrad research]]
   Why: Both evaluate RL approaches for agent improvement

Apply these? (y/N, or pick numbers: 1,3)
```

### Step 7: Apply on Confirmation

If user confirms:
1. Add new `[[wikilinks]]` to `{links_section}` section via `obsidian append` or `mcp__obsidian__str_replace`
2. If MOC suggestion — add note link to the MOC via `obsidian append`
3. Verify with `obsidian backlinks`

## Gotchas

- **"Unable to connect to main process"** — Obsidian IPC hung. Fix: quit Obsidian (Cmd+Q), reopen, wait 3 seconds, retry

- Maximum 5-7 suggestions — don't overwhelm
- Don't suggest links to orphan notes (they need their own fixing first)
- Ghost notes are NORMAL — don't flag `[[Technology]]` as "unresolved"
- Don't suggest connections that are too generic (e.g. both mention "Claude" — that's not meaningful)
- CLI first, MCP only for str_replace in middle of file
- NEVER auto-apply without user confirmation

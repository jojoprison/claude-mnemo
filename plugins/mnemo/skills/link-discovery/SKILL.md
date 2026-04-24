---
name: link-discovery
description: "Use automatically after creating any new Obsidian note to surface hidden connections with existing notes. Also use whenever the user asks 'find related notes', 'are there similar notes', 'connect this to others', or reviews a note for cross-references. Shows ranked suggestions with 'why relevant' explanations — does NOT auto-apply."
user-invocable: false
model: sonnet
context: fork
---

# mnemo:connect — Discover Hidden Links

Analyze a note and discover connections to other notes in the vault that aren't linked yet.

## Prerequisites & config

Obsidian must be open. Config at `~/.mnemo/config.json` — reads `vault` and `links_section`. Schema in `references/config-schema.md`.

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

### Step 3: Search for Related Notes + Backlinks (single grep + backlinks, parallel)

**Even better than parallel `obsidian search` calls: one `grep -E` with all concepts OR'd together.** Single filesystem scan against the vault path — ~50ms for any number of concepts vs ~180ms per `obsidian search`.

```bash
# Get vault filesystem path once
VAULT_PATH=$(obsidian vault vault="{vault}" | awk '/^path\s/{print $2}')

# Run these TWO commands in parallel (single message, two Bash tool uses):
# 1. Single grep for all concepts — much faster than N separate obsidian searches
grep -rlE --include="*.md" "({concept_1}|{concept_2}|...|{concept_N})" "$VAULT_PATH" 2>/dev/null

# 2. Backlinks check
obsidian backlinks file="{note_name}" vault="{vault}"
```

Collect matching notes from grep output (strip vault path prefix to get note names). Exclude the target note itself. Backlinks output → notes already connected (exclude from suggestions).

**Why not `obsidian search` per concept:** each CLI call is ~180ms. Single grep = ~50ms total for any N. On 7 concepts: 1.26s → 50ms (**25x faster**).

### Step 4: Generate Suggestions

Compare: notes found by search MINUS notes already linked (wikilinks + backlinks).

For each suggestion, explain WHY it's relevant (shared concept, shared tag, complementary topics).

### Step 5: Present (DO NOT auto-apply)

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

### Step 6: Apply on Confirmation

If user confirms:
1. Add new `[[wikilinks]]` to `{links_section}` section via **`mcp__obsidian__str_replace`** (preferred — targeted insert into the links section). CLI `obsidian append content="- [[name]]"` is a safe fallback only for plain wikilinks (no backticks, no `$()`)
2. If MOC suggestion — add note link to the MOC via `mcp__obsidian__str_replace` or `obsidian append` (plain wikilink = safe)
3. Verify with `obsidian backlinks`

**Why MCP preferred:** if suggestions ever include code-reference links with backticks (e.g. `[[function_name()]]`), CLI `obsidian append content="..."` would trigger zsh command substitution. MCP passes content as JSON — always safe.

## Gotchas

Common failures in `references/gotchas.md`. Tool-routing rationale in `references/tool-routing.md`. Skill-specific rules:

- **Max 5-7 suggestions** — don't overwhelm. If you find more, rank and present top-7.
- **Don't suggest links to orphan notes** — they need their own fixing first (run `/mn:health` if interested).
- **Ghost notes are normal** — `[[Technology]]` pointing to a non-existent note enables entity discovery. Not "unresolved" in the bad sense.
- **Avoid generic connections** — "both mention Claude" is noise. A connection is meaningful if it shares a concept, approach, or unresolved question.
- **Never auto-apply** — always ask the user before writing new wikilinks.

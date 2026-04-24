# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2026-04-24

### Changed — Tiered model selection (~60% latency reduction on common ops)

Every skill declared `model: opus` in v0.5.x. Opus is the slowest tier and overkill for index lookups and fixed-workflow classification. Retuned:

| Skill | Before | After | Rationale |
|-------|--------|-------|-----------|
| `/mn:health` | opus | **haiku** | Deterministic CLI outputs → formatted report, no synthesis |
| `/mn:connect` | opus | **haiku** | Mechanical search + backlinks diff, no judgment calls |
| `/mn:sort` | opus | **haiku** | Rule-based classification against a fixed taxonomy |
| `/mn:setup` | opus | **haiku** | Interactive Q&A, one-time |
| `/mn:ask` | opus | **sonnet** | Light synthesis from N notes — Sonnet 4.6 is plenty |
| `/mn:save` | opus | **sonnet** | Classify + cascade to 4 backends |
| `/mn:session` | opus | **sonnet** | Summarize + MCP write + handoff update |
| `/mn:review` | opus | **opus** (kept) | Session-completeness analysis + skill-gap reasoning genuinely needs Opus |

### Changed — No more `context: fork` on index-only skills

`context: fork` spins up a fresh Claude session with a cold cache. Kept only on skills that process large vault context (`/mn:save`, `/mn:session`, `/mn:review` stays default). Removed from `/mn:ask`, `/mn:connect`, `/mn:health`, `/mn:sort`, `/mn:setup` — they reuse the current session's warm cache.

### Changed — Parallel CLI invocations

Three skills previously made sequential `obsidian` calls. Now documented as parallel (single assistant message, multiple Bash tool uses):

- **`/mn:ask`** Step 3 — all search terms in parallel (4×180ms → 180ms)
- **`/mn:ask`** Step 4 — read top-7 notes in parallel (7×185ms → 185ms)
- **`/mn:session`** Step 2 — exact-filename read + same-day search in parallel
- **`/mn:connect`** Step 3 — all concept searches + backlinks check in parallel (8×180ms → 180ms)

### Changed — `/mn:review` inline Python extracted

`session-review/SKILL.md` dropped from 387 to ~250 lines. The two inline Python heredocs (session JSONL scan + skill auto-discovery) moved to `plugins/mnemo/scripts/session-scan.py` and `skills-discover.py`. Each script now caches results to `/tmp/` (60s for session scan, 300s for skills inventory) — `/mn:review` reruns during the same session are instant instead of re-parsing the JSONL every time.

### Performance

Combined effect on a warm Claude Code instance:

| Operation | Before | After |
|-----------|--------|-------|
| `/mn:health` (400-note vault) | ~8s | ~3s |
| `/mn:ask` broad query | ~6s | ~2s |
| `/mn:connect` | ~7s | ~2.5s |
| `/mn:session` | ~5s | ~2.5s |
| `/mn:review` (rerun) | ~10s | ~3s (cached scan) |

## [0.5.10] - 2026-04-21

### Security

- **🚨 Fixed shell injection in `/mn:session`, `/mn:save`, `/mn:sort`, `/mn:setup`** — CLI `obsidian create content="..."` passes markdown through zsh double-quoted strings, which triggers command substitution on any backticks or `$(...)` inside code blocks. A real incident on 2026-04-21 accidentally executed `make deploy-back` on production because a session note contained a bash code block. (Harmless that time — same image SHA, no migrations — but a genuine vulnerability.)

### Changed — MCP-first hybrid tool routing

All write operations with arbitrary markdown bodies are now routed through MCP (`mcp__obsidian__create`, `mcp__obsidian__str_replace`, `mcp__obsidian__insert`) instead of CLI. Read/search/orphans/backlinks stay on CLI — they're faster (indexed) and unique to CLI. Benchmark on this machine:

| Operation | CLI | MCP |
|-----------|-----|-----|
| create | ~180 ms (node cold-start) | ~30-50 ms |
| search | ~175 ms (indexed) | not available |
| read | ~185 ms | similar |
| orphans/backlinks/tags | ~180 ms | not available |

Rule of thumb: **any `content=` arg with markdown → MCP; everything else → CLI**.

### Changed — session duplicate detection

`/mn:session` Step 2 became two-level:

1. **Exact filename read** (`obsidian read file="{planned-name}"`) — if the note exists, ask append/overwrite/rename
2. **Related same-day search** (`obsidian search query="{prefix}{date}"`) — show informational list so the user can cross-link, but don't block creation

Frontmatter now includes `session_id: {CLAUDE_SESSION_ID}` — disambiguates same-day sessions when topic keywords overlap.

### Changed — handoff updates are targeted

`/mn:session` Step 5 uses `mcp__obsidian__str_replace` to update specific sections of `Meta — Session Handoff` instead of blind `obsidian append`. Handoff no longer accumulates stale pending items.

### Changed — inbox/memory/setup notes

- `/mn:save` — Atom/Molecule/Source creation via `mcp__obsidian__create`
- `/mn:sort` — reclassified notes created via MCP
- `/mn:setup` — `Meta — Session Handoff` bootstrapped via MCP
- `/mn:connect` — prefer `mcp__obsidian__str_replace` for adding `[[wikilinks]]` to the links section

### Fixed

- Removed stale "skill unsafe — don't invoke" ban from global `~/.claude/CLAUDE.md`. `/mn:session` is safe to use again as of this release.

## [0.5.9] - 2026-04-07

### Changed
- **`/mn:review` is now an end-of-session orchestrator** — auto-runs save + session without asking
  - Detects unsaved decisions → auto-invokes `mnemo:memory-routing`
  - Detects no session notes → auto-invokes `mnemo:session-notes`
  - Remaining skills (commit, connect, health, sort) → asks before running
  - Skip auto-run if skill was already invoked this session
  - Only command users need at session end
- Improved skill descriptions for better auto-triggering (pushy pattern from skill-creator)
- docs/review.md updated with orchestrator workflow

## [0.5.8] - 2026-04-07

### Breaking Changes
- **Plugin name reverted to `mnemo`** (was `mn` in 0.4.0). Autocomplete now shows `(mnemo)` label.
- **Skill directories renamed** — internal names changed (e.g. `session` → `session-notes`). User-facing commands (`/mn:session`) unchanged.

### Added
- **Skill-aware session review** (`/mn:review`) — complete rewrite:
  - JSONL session introspection via `${CLAUDE_SESSION_ID}` preprocessing
  - Auto-discovers 200+ installed skills across 6 glob paths
  - Session fingerprinting: implementation, research, debugging, refactoring, documentation, configuration, planning
  - Skill gap analysis with trigger matrix per session type
  - Execution chain — offers to run missed skills in priority order
  - Inline execution (no `context: fork`) for conversation access + skill invocation
- **SessionStart cleanup hook** — automatically removes stale plugin cache versions on every Claude Code launch. No more autocomplete ghosts from old versions.

### Changed
- **CE-pattern naming** — plugin name `mnemo` + command prefix `mn:` (same pattern as compound-engineering `ce:` prefix). Type `/mn:` to see all commands with `(mnemo)` label.
- **Skills hidden from autocomplete** — `user-invocable: false` + unique directory names prevent duplicate entries. Commands (`/mn:*`) are the sole user-facing UI.
- **Skill directories renamed** to avoid autocomplete collision with commands:
  - `session` → `session-notes`
  - `save` → `memory-routing`
  - `review` → `session-review`
  - `ask` → `vault-search`
  - `health` → `vault-health`
  - `connect` → `link-discovery`
  - `sort` → `inbox-triage`
  - `setup` → `initial-setup`
- Cross-references updated: `/mn:` → `/mnemo:` in all skill files
- Stale references removed: `dump`, `check-gmail`, `gmail_enabled` config

### Technical Notes
- Skill tool resolves by **directory name**, not frontmatter `name` field — both must match
- `disable-model-invocation: true` shows in autocomplete (counterintuitive); `user-invocable: false` hides from autocomplete
- Default (no flags) = `user-invocable: true`

## [0.4.0] - 2026-03-28

### Added
- `/mn:` command aliases for autocomplete — 8 thin command wrappers in `commands/mn/`
- `mnemo:review` skill — session completeness analyzer

### Changed
- Plugin renamed `mnemo` → `mn` for shorter invocation (reverted in 0.5.8)
- Removed `dump` and `check-gmail` skills (consolidated into `save` and external `gws`)
- Skill count: 9 → 8

## [0.3.0] - 2026-03-24

### Added
- `mnemo:save` — memory routing cascade with graceful degradation
  - Routes to: Obsidian → claude-mem → memory/ → CLAUDE.md
  - Each backend independent — if one fails, others still work
  - Auto-classifies input (fact→Atom, insight→Molecule, decision, gotcha, source)
  - Configurable via `cascade` section in config.json

### Changed
- All skills: IPC error handling (v0.2.4)
- health: tag-based counting (v0.2.4)
- Skill count: 8 → 9

## [0.2.0] - 2026-03-24

### Added
- `mnemo:ask` — vault knowledge search with citation synthesis
- `mnemo:sort` — classify inbox notes into proper typed notes
- `mnemo:setup` — interactive onboarding
- `CONTRIBUTING.md`
- Config path unified: `~/.mnemo/config.json`
- `links_section` configurable

### Changed
- All skills: English code, localized examples
- health: specific CLI commands for all 8 audit steps
- session: MOC verification, handoff update, orphan check

## [0.1.0] - 2026-03-23

### Added
- Initial release with 5 skills: health, connect, dump, session, check-gmail
- Plugin marketplace support
- `config.example.json`
- MIT License

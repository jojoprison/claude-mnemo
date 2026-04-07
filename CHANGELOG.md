# Changelog

All notable changes to this project will be documented in this file.

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

# Changelog

All notable changes to this project will be documented in this file.

## [0.5.4] - 2026-04-07

### Changed
- **Plugin name reverted to `mnemo`** — fixes `mn:mn:` duplication in autocomplete
  - Autocomplete: `/mn:save (mnemo)`, `/mn:review (mnemo)` — CE pattern
  - Expansion: `mnemo:mn:save` (full qualified name)
- **Skills hidden from autocomplete** — `disable-model-invocation: true` on all SKILL.md
  - No duplicate entries (`/save` vs `/mn:save`)
  - Skills still callable via Skill tool from commands
  - Commands are the sole user-facing UI
- **`mnemo:review` rewritten** — skill-aware session completeness analyzer
  - JSONL session introspection via `${CLAUDE_SESSION_ID}` preprocessing
  - Auto-discovers 200+ installed skills across 6 glob paths
  - Session fingerprinting (implementation/research/debugging/refactoring/docs/config)
  - Skill gap analysis with trigger matrix per session type
  - Execution chain — runs missed skills in priority order
  - Inline (no `context: fork`) for conversation access + skill execution
- Cross-references updated: `/mn:` → `/mnemo:` in all skill files
- Stale references removed: `/mn:dump`, `/mn:check-gmail`
- Plugin version: 0.4.0 → 0.5.4

## [0.4.0] - 2026-03-28

### Added
- `/mn:` command aliases for autocomplete — 8 thin command wrappers in `commands/mn/`
  - `/mn:session`, `/mn:save`, `/mn:ask`, `/mn:health`, `/mn:sort`, `/mn:connect`, `/mn:setup`, `/mn:review`
  - Same pattern as compound-engineering `/ce:` prefix
  - Commands delegate to corresponding skills via Skill tool
  - Enables autocomplete dropdown when typing `/mn:` in Claude Code
- `mnemo:review` skill — session completeness analyzer
  - Scans conversation for done items, missed items, hanging threads
  - Outputs actionable table with follow-up recommendations
- Plugin renamed `mnemo` → `mn` for shorter invocation

### Changed
- Removed `dump` and `check-gmail` skills (consolidated into `save` and external `gws`)
- Skill count: 9 → 8 (dump/check-gmail removed, review added)

## [0.3.0] - 2026-03-24

### Added
- `mnemo:save` — memory routing cascade with graceful degradation
  - Routes to: Obsidian → claude-mem → memory/ → CLAUDE.md
  - Each backend independent — if one fails, others still work
  - Auto-classifies input (fact→Atom, insight→Molecule, decision, gotcha, source)
  - Configurable via `cascade` section in config.json
- `cascade` config section for enabling/disabling memory backends
- docs/save.md with full documentation

### Changed
- All skills: IPC error handling in Gotchas (v0.2.4)
- health: tag-based counting instead of unreliable fulltext search (v0.2.4)
- check-gmail: correct gws command `+triage` (v0.2.3)
- Skill count: 8 → 9

## [0.2.1] - 2026-03-24

### Changed
- Renamed `mnemo:check-mail` → `mnemo:check-gmail` (only works with Gmail via gws CLI)
- Updated all references across README, CHANGELOG, setup skill

## [0.2.0] - 2026-03-24

### Added
- `mnemo:ask` — vault knowledge search with citation synthesis
- `mnemo:sort` — classify inbox notes into proper typed notes (atom, molecule, source...)
- `mnemo:setup` — interactive onboarding (vault name, taxonomy, language, integrations)
- `CONTRIBUTING.md` — guide for adding new skills
- Config path unified: `~/.mnemo/config.json`
- `links_section` configurable (supports `## Links`, `## Связи`, custom)
- Auto-tags extraction in `mnemo:dump` (max 2 from content)

### Changed
- All skills: English code, localized examples in README
- `mnemo:health`: specific CLI commands for all 8 audit steps
- `mnemo:session`: added MOC verification, session handoff update, orphan check
- README: full Russian section mirroring English with all 8 skills
- Version bumped from 0.1.0 to 0.2.0

## [0.1.0] - 2026-03-23

### Added
- Initial release with 5 skills:
  - `mnemo:health` — vault audit (orphans, broken links, analytics, stale notes)
  - `mnemo:connect` — hidden link discovery between notes
  - `mnemo:dump` — zero-friction brain dump (inbox capture)
  - `mnemo:session` — session summary notes + cross-session handoff
  - `mnemo:check-gmail` — Gmail → Obsidian bridge with deadline detection
- Plugin marketplace support (`claude plugin marketplace add`)
- `config.example.json` with taxonomy configuration
- README with English and Russian documentation
- MIT License

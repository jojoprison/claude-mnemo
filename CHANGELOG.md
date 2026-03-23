# Changelog

All notable changes to this project will be documented in this file.

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
  - `mnemo:check-mail` — Gmail → Obsidian bridge with deadline detection
- Plugin marketplace support (`claude plugin marketplace add`)
- `config.example.json` with taxonomy configuration
- README with English and Russian documentation
- MIT License

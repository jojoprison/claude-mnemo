# claude-mnemo

> Persistent memory layer for Claude Code — your Obsidian vault on autopilot.

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet?style=flat-square)](https://claude.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-5-blue?style=flat-square)](plugins/mnemo/skills/)

**[English](#-what-it-does)** | **[Русский](#-что-делает)**

---

## What It Does

**mnemo** gives Claude Code a persistent memory through your Obsidian vault. Five skills that handle the boring parts of knowledge management so you can focus on thinking.

Most "second brain" tools assume you have time to organize. mnemo assumes you don't.

```
You work → mnemo remembers → Your vault grows → You find things later
```

### The Skills

| Skill | Command | What it does |
|-------|---------|-------------|
| **health** | `/mnemo:health` | Vault audit: orphans, broken links, missing sections, stale notes, growth stats |
| **connect** | `/mnemo:connect` | Discovers hidden connections between notes you'd never think of |
| **dump** | `/mnemo:dump` | Zero-friction brain dump — capture now, classify later |
| **session** | `/mnemo:session` | Auto-generates session summary + cross-session handoff |
| **check-mail** | `/mnemo:check-mail` | Gmail → Obsidian bridge with deadline detection |

### Why Not Just Use Obsidian Plugins?

Obsidian plugins run inside Obsidian. mnemo runs inside **Claude Code** — it has access to your entire development context, your conversation history, and your codebase. When you finish a 3-hour debugging session, `/mnemo:session` knows what you did because it was there.

## Architecture

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  Claude Code  │────▶│  mnemo skills  │────▶│  Obsidian CLI │
│  (you talk)   │     │  (5 skills)    │     │  (vault ops)  │
└──────────────┘     └───────────────┘     └──────────────┘
                            │
                      config.json
                     (vault name,
                      taxonomy)
```

**Key design decisions:**
- **CLI-first** — uses `obsidian` CLI commands, not MCP ([70,000x cheaper](https://x.com/kepano))
- **Config-driven** — vault name, taxonomy, rules in `config.json` (gitignored)
- **Non-destructive** — skills report and suggest, never auto-delete or overwrite
- **Any taxonomy** — works with Zettelkasten, PARA, Atom/Molecule, or your own system

## Quick Start

### Option 1: Plugin Marketplace (recommended)

```bash
claude plugin marketplace add jojoprison/claude-mnemo
claude plugin install mnemo@claude-mnemo
```

### Option 2: Direct Install

```bash
claude plugin install github:jojoprison/claude-mnemo
```

### Option 3: Manual (skills only)

```bash
# Clone into your plugins directory
git clone https://github.com/jojoprison/claude-mnemo.git ~/.claude/plugins/claude-mnemo
```

### First Run

After install, run any skill — it will ask for your vault name on first use and save to `config.json`:

```
/mnemo:health
> What's your Obsidian vault name? main
> Saved to config.json. Running health check...
```

## Usage Examples

### Weekly vault checkup

```
/mnemo:health
```

```
📊 Vault Health Report (2026-03-23)

Total: 487 notes
  Atoms: 89 | Molecules: 23 | Sources: 34
  Sessions: 67 | MOCs: 14 | Inbox: 4

🔴 Orphans: 3
  - Atom — old note without links
🟡 Missing ## Связи: 2
📬 Inbox backlog: 4 notes waiting for classification
🏆 Top-5 Hubs: MOC — Security (34), MOC — AI ML Tools (28)...
```

### Quick capture on the go

```
/mnemo:dump "idea: use HisPO from LongCat for pipeline stabilization"
```

```
📬 Saved: "Inbox — HisPO for pipeline stabilization"
   Classify later with /mnemo:health
```

### Discover hidden links

```
/mnemo:connect "Atom — LongCat-Flash-Prover"
```

```
🔗 Connection suggestions for "Atom — LongCat-Flash-Prover"

Already connected: 3 notes
New suggestions: 2

1. [[Atom — SCOPE beats TextGrad]]
   Why: Both discuss agentic RL stability

2. [[MOC — Agent Self-Correction]]
   Why: trial→verify→reflect cycle matches SCOPE pattern

Apply these? (y/N, or pick numbers: 1,2)
```

### End-of-session save

```
/mnemo:session
```

Creates a full session note, updates the relevant MOC, and writes handoff context for the next session.

### Check email

```
/mnemo:check-mail
```

```
📬 Email check complete
Scanned: 10 unread | Saved: 2 important | Skipped: 8
Deadlines found: 1 (added to daily note)
```

## Configuration

Copy `config.example.json` to your skill directory as `config.json`:

```json
{
  "vault": "main",
  "taxonomy": {
    "atom": { "prefix": "Atom — ", "tag": "atom" },
    "molecule": { "prefix": "Molecule — ", "tag": "molecule" },
    "source": { "prefix": "Source — ", "tag": "source" },
    "session": { "prefix": "Session — ", "tag": "session" },
    "moc": { "prefix": "MOC — ", "tag": "moc" },
    "inbox": { "prefix": "Inbox — ", "tag": "inbox" }
  },
  "handoff_note": "Meta — Session Handoff",
  "gmail_mark_read": false,
  "cli_first": true
}
```

**All fields are optional.** Skills will ask on first use and save defaults.

### Custom Taxonomy

mnemo doesn't force a note structure. Change `taxonomy` in config to match yours:

```json
{
  "taxonomy": {
    "permanent": { "prefix": "", "tag": "permanent" },
    "fleeting": { "prefix": "F: ", "tag": "fleeting" },
    "literature": { "prefix": "L: ", "tag": "literature" }
  }
}
```

## Requirements

- [Claude Code](https://claude.ai/code) (Pro, Max, or Team subscription)
- [Obsidian](https://obsidian.md) (free) — **must be running**
- [Obsidian CLI](https://github.com/kepano/obsidian-cli) — `obsidian` command in PATH
- [gws CLI](https://github.com/nicholasgasior/gws) — only for `mnemo:check-mail`

## Project Structure

```
claude-mnemo/
├── .claude-plugin/
│   └── marketplace.json         # Marketplace manifest
├── plugins/
│   └── mnemo/
│       ├── .claude-plugin/
│       │   └── plugin.json      # Plugin manifest
│       └── skills/
│           ├── health/SKILL.md    # /mnemo:health
│           ├── connect/SKILL.md   # /mnemo:connect
│           ├── dump/SKILL.md      # /mnemo:dump
│           ├── session/SKILL.md   # /mnemo:session
│           └── check-mail/SKILL.md # /mnemo:check-mail
├── config.example.json          # Config template
├── README.md
└── LICENSE
```

## Inspired By

- [My-Brain-Is-Full-Crew](https://github.com/gnekt/My-Brain-Is-Full-Crew) — 8 AI agents managing Obsidian (great concept, different architecture: PARA-based, heavier, full vault takeover). mnemo takes the best ideas (agent coordination, vault health, connection discovery) and packages them as lightweight skills that work with **any** existing vault structure.
- [kepano/obsidian-cli](https://github.com/kepano/obsidian-cli) + [obsidian-skills](https://github.com/kepano/obsidian-skills) — CLI-first philosophy and the 70,000x token savings insight.
- [Zettelkasten](https://zettelkasten.de/), [Atomic/Molecular Notes](https://reasonabledeviations.com/2022/04/18/molecular-notes-part-1/), [Maps of Content](https://www.dsebastien.net/2022-05-15-maps-of-content/) — note taxonomy research.

## Contributing

PRs welcome. If you have a better prompt pattern, a new skill idea, or a taxonomy adapter — open a PR.

---

# Русский

## Что делает

**mnemo** дает Claude Code постоянную память через Obsidian vault. Пять скиллов, которые берут на себя рутину управления знаниями.

Большинство инструментов «второго мозга» предполагают, что у тебя есть время всё организовать. mnemo предполагает, что нет.

### Скиллы

| Скилл | Команда | Что делает |
|-------|---------|-----------|
| **health** | `/mnemo:health` | Аудит vault: orphans, broken links, отсутствующие секции, стагнирующие заметки, статистика |
| **connect** | `/mnemo:connect` | Находит скрытые связи между заметками |
| **dump** | `/mnemo:dump` | Brain dump без классификации — захвати сейчас, классифицируй потом |
| **session** | `/mnemo:session` | Автоматическая сессионная заметка + cross-session handoff |
| **check-mail** | `/mnemo:check-mail` | Gmail → Obsidian с обнаружением дедлайнов |

## Установка

### Вариант 1: Plugin Marketplace (рекомендуется)

```bash
claude plugin marketplace add jojoprison/claude-mnemo
claude plugin install mnemo@claude-mnemo
```

### Вариант 2: Прямая установка

```bash
claude plugin install github:jojoprison/claude-mnemo
```

### Вариант 3: Вручную

```bash
git clone https://github.com/jojoprison/claude-mnemo.git ~/.claude/plugins/claude-mnemo
```

## Конфигурация

Скопируй `config.example.json` → `config.json` в директорию скилла. Все поля опциональны — скиллы спросят при первом запуске.

Поддерживает любую таксономию заметок: Zettelkasten, PARA, Atom/Molecule, или твою собственную.

## Требования

- [Claude Code](https://claude.ai/code) (подписка Pro, Max или Team)
- [Obsidian](https://obsidian.md) (бесплатно) — **должен быть запущен**
- [Obsidian CLI](https://github.com/kepano/obsidian-cli) — команда `obsidian` в PATH
- [gws CLI](https://github.com/nicholasgasior/gws) — только для `mnemo:check-mail`

## Вдохновение

- [My-Brain-Is-Full-Crew](https://github.com/gnekt/My-Brain-Is-Full-Crew) — 8 AI-агентов для Obsidian. mnemo берет лучшие идеи (координация, здоровье vault, поиск связей) и упаковывает в легковесные скиллы, совместимые с **любой** существующей структурой vault.
- [kepano/obsidian-cli](https://github.com/kepano/obsidian-cli) — CLI-first философия.

---

Made with Claude Code by [jojoprison](https://github.com/jojoprison)

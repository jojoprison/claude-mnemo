# claude-mnemo

> Persistent memory layer for Claude Code — your Obsidian vault on autopilot.

[![Claude Code](https://img.shields.io/badge/Claude_Code-plugin-blueviolet?style=flat-square)](https://claude.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-8-blue?style=flat-square)](plugins/mnemo/skills/)
[![Obsidian](https://img.shields.io/badge/Obsidian-compatible-7C3AED?style=flat-square&logo=obsidian&logoColor=white)](https://obsidian.md)

**[English](#-what-it-does)** | **[Русский](#-что-делает)**

---

## 🧠 What It Does

**mnemo** gives Claude Code a persistent memory through your Obsidian vault. Eight skills that handle the boring parts of knowledge management so you can focus on thinking.

Most "second brain" tools assume you have time to organize. mnemo assumes you don't.

```
You work → mnemo remembers → Your vault grows → You find things later
```

### The Skills

| Skill | Command | What it does |
|-------|---------|-------------|
| 🏥 **health** | `/mnemo:health` | Vault audit: orphans, broken links, missing sections, stale notes, growth stats |
| 🔍 **ask** | `/mnemo:ask` | Search vault and synthesize answers from multiple notes with citations |
| 🔗 **connect** | `/mnemo:connect` | Discovers hidden connections between notes you'd never think of |
| 📥 **dump** | `/mnemo:dump` | Zero-friction brain dump — capture now, classify later |
| 📂 **sort** | `/mnemo:sort` | Classify inbox notes into proper types (atom, molecule, source...) |
| 📝 **session** | `/mnemo:session` | Auto-generates session summary + cross-session handoff |
| 📬 **check-gmail** | `/mnemo:check-gmail` | Gmail → Obsidian bridge with deadline detection |
| ⚙️ **setup** | `/mnemo:setup` | Interactive onboarding — vault name, taxonomy, language, integrations |

### Why Not Just Use Obsidian Plugins?

Obsidian plugins run inside Obsidian. mnemo runs inside **Claude Code** — it has access to your entire development context, your conversation history, and your codebase. When you finish a 3-hour debugging session, `/mnemo:session` knows what you did because it was there.

## 🏗 Architecture

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  Claude Code  │────▶│  mnemo skills  │────▶│  Obsidian CLI │
│  (you talk)   │     │  (8 skills)    │     │  (vault ops)  │
└──────────────┘     └───────────────┘     └──────────────┘
                            │
                    ~/.mnemo/config.json
                     (vault, taxonomy,
                      links section)
```

**Key design decisions:**
- **CLI-first** — uses `obsidian` CLI commands, not MCP ([70,000x cheaper](https://x.com/kepano))
- **Config-driven** — vault name, taxonomy, rules in `config.json` (gitignored)
- **Non-destructive** — skills report and suggest, never auto-delete or overwrite
- **Any taxonomy** — works with Zettelkasten, PARA, Atom/Molecule, or your own system

## 🚀 Quick Start

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
git clone https://github.com/jojoprison/claude-mnemo.git ~/.claude/plugins/claude-mnemo
```

### First Run

After install, run any skill — it will ask for your vault name on first use and save to `config.json`:

```
/mnemo:health
> What's your Obsidian vault name? main
> Saved to config.json. Running health check...
```

## 📖 Usage Examples

### 🏥 Weekly vault checkup

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

### 📥 Quick capture on the go

```
/mnemo:dump "idea: use HisPO from LongCat for pipeline stabilization"
```

```
📬 Saved: "Inbox — HisPO for pipeline stabilization"
   Classify later with /mnemo:health
```

### 🔗 Discover hidden links

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

### 📝 End-of-session save

```
/mnemo:session
```

Creates a full session note with frontmatter, tags, and `## Связи` section. Automatically:
- Verifies the note is linked in the relevant MOC
- Updates the cross-session handoff file (`Meta — Session Handoff`)
- Checks for orphans after creation

### 📬 Check email

```
/mnemo:check-gmail
```

```
📬 Email check complete
Scanned: 10 unread | Saved: 2 important | Skipped: 8
Deadlines found: 1 (added to daily note)
```

## ⚙️ Configuration

Run `/mnemo:setup` for interactive configuration, or copy `config.example.json` manually:

```bash
mkdir -p ~/.mnemo
cp config.example.json ~/.mnemo/config.json
# Edit ~/.mnemo/config.json with your values
```

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
  "links_section": "## Links",
  "handoff_note": "Meta — Session Handoff",
  "gmail_enabled": false,
  "gmail_mark_read": false
}
```

**All fields are optional.** Run `/mnemo:setup` to configure interactively, or skills will ask on first use.

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

## 🔄 Cross-Session Continuity

The killer feature. When a session ends, `/mnemo:session` writes a handoff note:

```markdown
## Pending
- [ ] Check orphans after mass note creation (project: research, date: 2026-03-23)
- [ ] Update MOC — AI Research with 3 new notes

## Context
- Researched WeChat agent ecosystem, all saved in Session — 2026-03-23
- Reported malware repo, waiting for GitHub response
```

Next session reads this file and picks up where you left off. No more "what was I doing yesterday?"

## 📋 Requirements

- [Claude Code](https://claude.ai/code) (any auth: Pro/Max/Team subscription or API key)
- [Obsidian](https://obsidian.md) (free) — **must be running**
- [Obsidian CLI](https://github.com/kepano/obsidian-cli) — `obsidian` command in PATH
- [gws CLI](https://github.com/nicholasgasior/gws) — only for `mnemo:check-gmail`

## 📁 Project Structure

```
claude-mnemo/
├── .claude-plugin/
│   └── marketplace.json         # Marketplace manifest
├── plugins/
│   └── mnemo/
│       ├── .claude-plugin/
│       │   └── plugin.json      # Plugin manifest
│       └── skills/
│           ├── health/SKILL.md     # /mnemo:health — vault audit
│           ├── ask/SKILL.md        # /mnemo:ask — knowledge search
│           ├── connect/SKILL.md    # /mnemo:connect — link discovery
│           ├── dump/SKILL.md       # /mnemo:dump — quick capture
│           ├── sort/SKILL.md       # /mnemo:sort — inbox triage
│           ├── session/SKILL.md    # /mnemo:session — session notes
│           ├── check-gmail/SKILL.md # /mnemo:check-gmail — Gmail bridge
│           └── setup/SKILL.md      # /mnemo:setup — onboarding
├── config.example.json           # Config template
├── CONTRIBUTING.md               # How to add skills
├── README.md
└── LICENSE
```

## 💡 Inspired By

- [My-Brain-Is-Full-Crew](https://github.com/gnekt/My-Brain-Is-Full-Crew) — 8 AI agents managing Obsidian (great concept, different architecture: PARA-based, heavier, full vault takeover). mnemo takes the best ideas (agent coordination, vault health, connection discovery) and packages them as lightweight skills that work with **any** existing vault structure.
- [kepano/obsidian-cli](https://github.com/kepano/obsidian-cli) + [obsidian-skills](https://github.com/kepano/obsidian-skills) — CLI-first philosophy and the 70,000x token savings insight.
- [Zettelkasten](https://zettelkasten.de/), [Atomic/Molecular Notes](https://reasonabledeviations.com/2022/04/18/molecular-notes-part-1/), [Maps of Content](https://www.dsebastien.net/2022-05-15-maps-of-content/) — note taxonomy research.

## 🤝 Contributing

PRs welcome. If you have a better prompt pattern, a new skill idea, or a taxonomy adapter — open a PR.

---

# 🇷🇺 Русский

## 🧠 Что делает

**mnemo** даёт Claude Code постоянную память через Obsidian vault. Восемь скиллов, которые берут на себя рутину управления знаниями, чтобы ты мог сосредоточиться на мышлении.

Большинство инструментов «второго мозга» предполагают, что у тебя есть время всё организовать. mnemo предполагает, что нет.

```
Ты работаешь → mnemo запоминает → Vault растёт → Ты находишь потом
```

### Скиллы

| Скилл | Команда | Что делает |
|-------|---------|-----------|
| 🏥 **health** | `/mnemo:health` | Аудит vault: orphans, broken links, пропущенные секции, стагнирующие заметки, статистика роста |
| 🔍 **ask** | `/mnemo:ask` | Поиск по vault и синтез ответа из нескольких заметок с цитатами |
| 🔗 **connect** | `/mnemo:connect` | Находит скрытые связи между заметками, о которых ты бы не подумал |
| 📥 **dump** | `/mnemo:dump` | Brain dump без классификации — захвати мысль сейчас, классифицируй потом |
| 📂 **sort** | `/mnemo:sort` | Классификация inbox-заметок в правильные типы (atom, molecule, source...) |
| 📝 **session** | `/mnemo:session` | Автоматическая сессионная заметка + cross-session handoff (передача контекста) |
| 📬 **check-gmail** | `/mnemo:check-gmail` | Gmail → Obsidian мост с обнаружением дедлайнов |
| ⚙️ **setup** | `/mnemo:setup` | Интерактивный онбординг — имя vault, таксономия, язык, интеграции |

### Почему не обычные плагины Obsidian?

Плагины Obsidian работают внутри Obsidian. mnemo работает внутри **Claude Code** — у него есть доступ ко всему контексту разработки, истории разговора и кодовой базе. Когда ты заканчиваешь 3-часовую сессию дебаггинга, `/mnemo:session` знает что ты делал, потому что был рядом.

## 🏗 Архитектура

```
┌──────────────┐     ┌───────────────┐     ┌──────────────┐
│  Claude Code  │────▶│  mnemo skills  │────▶│  Obsidian CLI │
│  (ты говоришь)│     │  (5 скиллов)   │     │  (операции)   │
└──────────────┘     └───────────────┘     └──────────────┘
                            │
                      config.json
                    (имя vault,
                     таксономия)
```

**Ключевые решения:**
- **CLI-first** — использует команды `obsidian` CLI, не MCP ([в 70,000x дешевле по токенам](https://x.com/kepano))
- **Config-driven** — имя vault, таксономия, правила в `config.json` (gitignored)
- **Неразрушающий** — скиллы отчитываются и предлагают, никогда не удаляют и не перезаписывают автоматически
- **Любая таксономия** — работает с Zettelkasten, PARA, Atom/Molecule, или твоей собственной системой

## 🚀 Установка

### Вариант 1: Plugin Marketplace (рекомендуется)

```bash
claude plugin marketplace add jojoprison/claude-mnemo
claude plugin install mnemo@claude-mnemo
```

### Вариант 2: Прямая установка

```bash
claude plugin install github:jojoprison/claude-mnemo
```

### Вариант 3: Вручную (только скиллы)

```bash
git clone https://github.com/jojoprison/claude-mnemo.git ~/.claude/plugins/claude-mnemo
```

### Первый запуск

После установки запусти любой скилл — он спросит имя vault при первом использовании и сохранит в `config.json`:

```
/mnemo:health
> Как называется твой Obsidian vault? main
> Сохранено в config.json. Запускаю проверку...
```

## 📖 Примеры использования

### 🏥 Еженедельная проверка vault

```
/mnemo:health
```

```
📊 Здоровье Vault (2026-03-23)

Всего: 487 заметок
  Atoms: 89 | Molecules: 23 | Sources: 34
  Sessions: 67 | MOCs: 14 | Inbox: 4

🔴 Orphans (сироты): 3
  - Atom — старая заметка без связей
🟡 Без секции ## Связи: 2
📬 Inbox: 4 заметки ждут классификации
🏆 Топ-5 хабов: MOC — Security (34), MOC — AI ML Tools (28)...
```

### 📥 Быстрый захват мысли

```
/mnemo:dump "идея: использовать HisPO из LongCat для стабилизации pipeline"
```

```
📬 Сохранено: "Inbox — HisPO для стабилизации pipeline"
   Классифицируй позже через /mnemo:sort
```

### 🔍 Поиск по базе знаний

```
/mnemo:ask "что мы решили по стратегии ценообразования?"
```

```
На основе вашего vault:

Стратегия ценообразования обсуждалась 14.03.2026 во время обзора pipeline.
Ключевые решения:
- Freemium модель с usage-based тарифами [Источник: Session — 2026-03-14 pipeline vision]
- Enterprise план за $99/мес отклонён как слишком низкий [Источник: Atom — pricing research]

📚 Источники (2 заметки):
1. [[Session — 2026-03-14 pipeline vision]]
2. [[Atom — pricing research]]
```

### 🔗 Поиск скрытых связей

```
/mnemo:connect "Atom — LongCat-Flash-Prover"
```

```
🔗 Предложения по связям для "Atom — LongCat-Flash-Prover"

Уже связано: 3 заметки
Новые предложения: 2

1. [[Atom — SCOPE beats TextGrad]]
   Почему: обе обсуждают стабильность agentic RL

2. [[MOC — Agent Self-Correction]]
   Почему: цикл trial→verify→reflect совпадает с паттерном SCOPE

Применить? (y/N, или выбери номера: 1,2)
```

### 📝 Сохранение сессии

```
/mnemo:session
```

Создаёт полную сессионную заметку с frontmatter, тегами и секцией `## Связи`. Автоматически:
- Проверяет что заметка добавлена в соответствующий MOC
- Обновляет файл cross-session handoff (`Meta — Session Handoff`)
- Проверяет orphans после создания

### 📂 Классификация inbox

```
/mnemo:sort
```

```
📬 Inbox заметка 1/4: "Inbox — HisPO для стабилизации pipeline"

Содержание: "идея: использовать HisPO из LongCat для стабилизации pipeline"

Предложенный тип: atom (один факт/концепт)
Предложенное имя: "Atom — HisPO алгоритм для стабилизации MoE обучения"
Предложенные теги: [atom, agentic-rl, moe, antomate]
Предложенный MOC: [[MOC — Agent Self-Correction]]

Действия:
  [1] Принять предложение
  [2] Изменить тип
  [3] Редактировать имя/теги
  [4] Пропустить
  [5] Удалить
```

### 📬 Проверка почты

```
/mnemo:check-gmail
```

```
📬 Проверка почты завершена
Просмотрено: 10 непрочитанных | Сохранено: 2 важных | Пропущено: 8
Дедлайны: 1 (добавлен в daily note)
```

## 🔄 Cross-Session Continuity (передача контекста)

Киллер-фича. Когда сессия заканчивается, `/mnemo:session` записывает handoff-заметку:

```markdown
## Pending
- [ ] Проверить orphans после массового создания заметок (project: research, date: 2026-03-23)
- [ ] Обновить MOC — AI Research, добавить 3 новые заметки

## Context
- Исследовал экосистему WeChat agent, всё в Session — 2026-03-23
- Зарепортил malware repo, ждём ответа GitHub
```

Следующая сессия читает этот файл и подхватывает с того места, где остановились. Больше никакого «а что я вчера делал?»

## ⚙️ Конфигурация

Запусти `/mnemo:setup` для интерактивной настройки, или скопируй конфиг вручную:

```bash
mkdir -p ~/.mnemo
cp config.example.json ~/.mnemo/config.json
# Отредактируй ~/.mnemo/config.json
```

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
  "links_section": "## Связи",
  "handoff_note": "Meta — Session Handoff",
  "gmail_enabled": false,
  "gmail_mark_read": false
}
```

**Все поля опциональны.** `/mnemo:setup` настроит интерактивно, или скиллы спросят при первом запуске.

### Своя таксономия

mnemo не навязывает структуру заметок. Измени `taxonomy` в конфиге:

```json
{
  "taxonomy": {
    "permanent": { "prefix": "", "tag": "permanent" },
    "fleeting": { "prefix": "F: ", "tag": "fleeting" },
    "literature": { "prefix": "L: ", "tag": "literature" }
  }
}
```

## 📋 Требования

- [Claude Code](https://claude.ai/code) (любая авторизация: подписка Pro/Max/Team или API ключ)
- [Obsidian](https://obsidian.md) (бесплатно) — **должен быть запущен**
- [Obsidian CLI](https://github.com/kepano/obsidian-cli) — команда `obsidian` в PATH
- [gws CLI](https://github.com/nicholasgasior/gws) — только для `mnemo:check-gmail`

## 📁 Структура проекта

```
claude-mnemo/
├── .claude-plugin/
│   └── marketplace.json         # Marketplace манифест
├── plugins/
│   └── mnemo/
│       ├── .claude-plugin/
│       │   └── plugin.json      # Plugin манифест
│       └── skills/
│           ├── health/SKILL.md     # /mnemo:health — аудит vault
│           ├── ask/SKILL.md        # /mnemo:ask — поиск по знаниям
│           ├── connect/SKILL.md    # /mnemo:connect — поиск связей
│           ├── dump/SKILL.md       # /mnemo:dump — быстрый захват
│           ├── sort/SKILL.md       # /mnemo:sort — классификация inbox
│           ├── session/SKILL.md    # /mnemo:session — сессионные заметки
│           ├── check-gmail/SKILL.md # /mnemo:check-gmail — Gmail мост
│           └── setup/SKILL.md      # /mnemo:setup — онбординг
├── config.example.json           # Шаблон конфигурации
├── CONTRIBUTING.md               # Как добавить скиллы
├── README.md
└── LICENSE
```

## 💡 Вдохновение

- [My-Brain-Is-Full-Crew](https://github.com/gnekt/My-Brain-Is-Full-Crew) — 8 AI-агентов для управления Obsidian (отличный концепт, но другая архитектура: PARA, тяжеловесный, полный захват vault). mnemo берёт лучшие идеи (координация агентов, здоровье vault, поиск связей) и упаковывает в легковесные скиллы, совместимые с **любой** существующей структурой vault.
- [kepano/obsidian-cli](https://github.com/kepano/obsidian-cli) + [obsidian-skills](https://github.com/kepano/obsidian-skills) — CLI-first философия и инсайт про экономию токенов в 70,000 раз.
- [Zettelkasten](https://zettelkasten.de/), [Atomic/Molecular Notes](https://reasonabledeviations.com/2022/04/18/molecular-notes-part-1/), [Maps of Content](https://www.dsebastien.net/2022-05-15-maps-of-content/) — исследование таксономий заметок.

## 🤝 Участие

PR приветствуются. Если у тебя есть лучший промпт-паттерн, идея нового скилла или адаптер таксономии — открывай PR.

---

Made with 🧠 by [Claude Code](https://claude.ai) + [jojoprison](https://github.com/jojoprison)

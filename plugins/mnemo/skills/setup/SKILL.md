---
name: setup
description: "Use on first install or when reconfiguring mnemo. Interactive onboarding that creates config.json with vault name, taxonomy, language preferences, and integration settings."
disable-model-invocation: true
model: opus
---

# mnemo:setup — Interactive Onboarding

First-time setup for mnemo. Creates config.json with all settings.

## Workflow

### Step 1: Welcome

```
🧠 Welcome to mnemo — persistent memory for Claude Code.

Let's set up your configuration. This takes about 30 seconds.
```

### Step 2: Vault Name

```
What's your Obsidian vault name?
(The name shown in Obsidian's vault switcher)
> main
```

Verify vault exists:
```bash
obsidian search query="test" vault="{input}"
```

If error → "Vault not found. Is Obsidian open? Check the vault name."

### Step 3: Note Taxonomy

```
Which note taxonomy do you use?

[1] Atom/Molecule/Source/Session/MOC (Zettelkasten-inspired)
[2] PARA (Projects/Areas/Resources/Archive)
[3] Custom (you'll define prefixes and tags)

> 1
```

Map selection to taxonomy config.

### Step 4: Links Section Name

```
What heading do you use for note cross-references?

[1] ## Связи (Russian)
[2] ## Links
[3] ## Related
[4] ## Connections
[5] Custom

> 1
```

### Step 5: Gmail Integration

```
Do you want to enable mnemo:check-gmail (Gmail → Obsidian)?
This requires gws CLI to be installed and authorized.

[y/N] > n
```

If yes, verify: `gws gmail list --max 1`

### Step 6: Save Config

Write `~/.mnemo/config.json`:

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

### Step 7: Create Handoff Note

```bash
obsidian create name="Meta — Session Handoff" vault="{vault}" content="---
type: meta
tags: [meta, handoff, cross-session]
---

# Meta — Session Handoff

Cross-session continuity file. Updated by mnemo:session.

## Pending

## Context
- mnemo setup completed on {date}
"
```

### Step 8: Done

```
🧠 mnemo is ready!

Your skills:
  /mnemo:health    — vault audit & analytics
  /mnemo:connect   — discover hidden links
  /mnemo:session   — session notes + handoff
  /mnemo:ask       — search & synthesize
  /mnemo:sort      — classify inbox notes
  /mnemo:save      — memory routing cascade
  /mnemo:review    — session completeness review

Config saved to: ~/.mnemo/config.json
Handoff note created: Meta — Session Handoff

Try: /mnemo:health
```

## Gotchas

- **Run once** — if config.json exists, ask before overwriting
- **Obsidian must be open** — verify during vault name step
- **Don't create vault structure** — mnemo works with existing vaults, doesn't impose folders
- **PARA taxonomy** — if selected, map to: project/area/resource/archive with appropriate prefixes

# mnemo:setup — Interactive Onboarding

## Overview

First-time configuration for mnemo. Creates `~/.mnemo/config.json` through an interactive conversation.

## Usage

```
/mn:setup
```

Run once after installing the plugin.

## What It Configures

| Setting | What it does | Example |
|---------|-------------|---------|
| Vault name | Which Obsidian vault to use | `main` |
| Taxonomy | Note type prefixes and tags | Atom/Molecule/PARA/Custom |
| Links section | Heading for cross-references | `## Links`, `## Связи` |
| Gmail | Enable/disable email bridge | `true`/`false` |

## Onboarding Flow

```
🧠 Welcome to mnemo!

1. What's your Obsidian vault name? → main
2. Which taxonomy? → [1] Atom/Molecule (Zettelkasten)
3. Links section heading? → [1] ## Связи
4. Enable Gmail? → [N]
5. Config saved to ~/.mnemo/config.json
6. Handoff note created in vault
```

## Generated Config

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

## Important Notes

- **Run once** — if config exists, asks before overwriting
- **Obsidian must be open** — verifies vault name by running a test search
- **Creates handoff note** — `Meta — Session Handoff` in your vault
- **Doesn't create vault structure** — works with your existing vault as-is

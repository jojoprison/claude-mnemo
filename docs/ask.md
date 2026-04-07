# mnemo:ask — Vault Knowledge Search & Synthesis

## Overview

Search across your entire vault and get a synthesized answer with source citations. Like having a research assistant who read all your notes.

## Usage

```
/mn:ask "what did we decide about the pricing strategy?"
/mn:ask "find everything about Docker deployment"
/mn:ask "summarize what we know about SCOPE engine"
```

## How It Works

1. Breaks your question into 2-4 search terms
2. Runs `obsidian search` for each term
3. Reads the top 7 most relevant notes
4. Synthesizes a clear answer citing specific notes
5. Lists all source notes with `[[wikilinks]]`

## Example Output

```
Based on your vault:

The pricing strategy was decided on 2026-03-14 during the pipeline review.
Key points:
- Freemium model with usage-based tiers
  [Source: Session — 2026-03-14 pipeline vision]
- Enterprise plan at $99/mo was rejected as too low
  [Source: Atom — pricing research]

📚 Sources (2 notes):
1. [[Session — 2026-03-14 pipeline vision]]
2. [[Atom — pricing research]]
```

## Important Notes

- **Only answers from your vault** — never hallucinated from general knowledge
- **Max 7 notes read** — prevents context overflow
- **CLI-first search** — uses `obsidian search`, not MCP

## Related Skills

- `/mn:connect` — after finding related notes, connect them
- `/mn:save` — capture follow-up ideas or findings from the answer

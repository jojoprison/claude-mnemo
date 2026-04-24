# Tool Routing — MCP-first hybrid

Rule of thumb: **any write with markdown body → MCP; everything else → CLI.**

## Routing table

| Operation | Tool | Why |
|-----------|------|-----|
| **Create note** (arbitrary markdown) | `mcp__obsidian__create` | Shell-safe — content passes as JSON parameter, no zsh expansion |
| **Edit middle of file** | `mcp__obsidian__str_replace` | Exact-match replace, shell-safe |
| **Insert at line** | `mcp__obsidian__insert` | Line-number-based, shell-safe |
| **View file** | `mcp__obsidian__view` or CLI `obsidian read` | Both work; CLI is ~180ms, MCP similar |
| **Search (fulltext)** | CLI `obsidian search` | **Only CLI has this** — indexed, ~175ms, not available in MCP |
| **Orphans / backlinks / tags / unresolved** | CLI `obsidian orphans` / `backlinks` / etc. | **Only CLI has these** — indexed graph queries |
| **Vault metadata** | CLI `obsidian vault` | Returns filesystem path, file count, size |
| **List files** | CLI `obsidian files` | Indexed |
| **Append plain wikilink** (no backticks) | CLI `obsidian append content="- [[Name]]"` | Safe — no backticks means no shell expansion |
| **Append with markdown body** | `mcp__obsidian__str_replace` or temp-file + CLI | CLI with inline content is unsafe |
| **Delete** | CLI `obsidian delete` | No content arg, safe |
| **Arbitrary JS** | `mcp__obsidian__obsidian_api` or CLI `obsidian eval` | Both work |

## Why CLI-first for read / search / index

| Operation | CLI (ms) | MCP (ms) | Notes |
|-----------|----------|----------|-------|
| search | ~175 | N/A | Only CLI — kepano benchmarked 70,000x cheaper than scanning |
| read | ~185 | ~150-200 | Similar; CLI avoids MCP handshake |
| orphans / backlinks | ~180 | N/A | Only CLI |
| tags / files | ~180 | N/A | Only CLI |
| create | ~180 (cold node start) | ~30-50 | MCP wins when you're creating content |

## Why MCP-first for writes with markdown

CLI `obsidian create content="..."` is executed inside a zsh double-quoted context. That means:

- **Backticks** `` `cmd` `` → shell runs `cmd`, substitutes output.
- **`$(cmd)`** → same, command substitution.
- **`$VAR`** → variable expansion.

A markdown code block inside the content is an **exploit** in disguise:

````
```bash
make deploy-back
```
````

If that string ends up in `content="..."`, zsh runs `make deploy-back`. This really happened on 2026-04-21 — session note content triggered accidental prod deploy.

**MCP has no shell.** Content flows as a JSON string to the MCP server → Obsidian's internal API → disk. Backticks and `$(...)` are preserved verbatim, treated as text.

## When CLI append is safe

Plain wikilink appends (no backticks, no `$()`):

```bash
obsidian append file="MOC — Memory Systems" vault="main" \
  content="- [[Atom — New Note]]"
```

This is how skills add MOC entries. It's fast, indexed, and bulletproof when the content is literally just `- [[Name]]`.

Anything with code blocks or shell metacharacters → switch to MCP `str_replace` or `insert`.

## Reading order of preference

1. **Search / index query** → CLI (only option).
2. **Write with markdown body** → MCP (safety).
3. **Plain wikilink append** → CLI (faster, indexed).
4. **Targeted edit to existing note** → MCP `str_replace`.
5. **Read (for diff / context)** → CLI (warm index).

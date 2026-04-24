# Shared Gotchas — mnemo skills

Common failure modes and their fixes. Any mnemo skill can reference this file instead of repeating the same block.

## Obsidian IPC hung — "Unable to connect to main process"

**Symptom:** `obsidian <anything>` returns `Error: Unable to connect to main process`.

**Cause:** Obsidian's CLI IPC socket crashed. The app might still look alive in the Dock but isn't accepting connections.

**Fix:**
1. Quit Obsidian fully: Cmd+Q (not just close the window).
2. Reopen Obsidian.
3. Wait ~3 seconds for the vault to finish indexing.
4. Retry the mnemo command.

## Obsidian must be open

All `obsidian` CLI commands and all `mcp__obsidian__*` tools require the running Obsidian app. Skills don't probe for this on every step — they fail-fast on the first IPC call and gracefully fall back when possible (e.g., memory-routing skips Obsidian and continues to claude-mem + memory/).

If a skill is supposed to only write (not search/read), check whether it can proceed offline: `memory-routing` and `save`-flavored skills degrade gracefully, search/connect/health skills can't.

## `/plugin update` — stale Stop hooks

After upgrading any plugin (claude-mem especially), already-open Claude Code windows continue to reference the OLD cache path:

```
Plugin directory does not exist: /Users/.../plugins/cache/thedotmack/claude-mem/10.5.2
```

**Why:** hook paths are captured at window-start time. Newer windows pick up the fresh version; older windows keep the stale path and fail on Stop.

**Fix:** close and reopen **all** Claude Code windows after any `/plugin install` or `/plugin update`. New windows inherit the updated `CLAUDE_PLUGIN_ROOT`.

Verify clean cache:
```bash
ls ~/.claude/plugins/cache/thedotmack/claude-mem/
# Should be ONE folder = current version. Multiple folders = restart windows.
```

## Shell injection via `obsidian create content="..."`

**Don't** pass markdown with code blocks through `obsidian create content="..."` or `obsidian append content="..."` from Bash. zsh expands backticks and `$(...)` inside double-quoted strings — a real 2026-04-21 incident accidentally ran `make deploy-back` on production because a session note contained a bash code block.

**Use instead:**
- `mcp__obsidian__create(path=..., file_text=...)` — content passes as JSON, shell uninvolved
- `mcp__obsidian__str_replace` / `mcp__obsidian__insert` for edits

**Safe CLI uses:** `obsidian search`, `obsidian read`, `obsidian orphans`, `obsidian backlinks`, `obsidian tags`, `obsidian vault`, plain-wikilink appends with no backticks.

## claude-mem worker not responding on 127.0.0.1:37777

`memory-routing` pings the local claude-mem worker when saving observations. If the port doesn't respond:

- **Most common cause:** claude-mem plugin isn't installed, or worker hasn't started yet after session boot (takes 5-10s).
- **Less common:** port collision. Reserved port per global CLAUDE.md — another process shouldn't be on 37777.

**Skill behavior:** log `⚠️ claude-mem: skipped (port 37777 not responding)` and continue with the other backends. Never fail the whole save.

## memory/ is NOT `./memory/`

`memory-routing` writes Claude-facing memory files. The target directory is:

```
~/.claude/projects/-{slugified-cwd}/memory/
```

**Never** write to `./memory/` in the project root — that puts auto-memory files into git.

Find the correct slug from the `MEMORY.md` path already loaded in the conversation context, or slugify the cwd (`/` → `-`, leading `-` kept).

## "Unable to connect" specifically on `mcp__obsidian__*` calls

Same root cause as CLI IPC hung — restart Obsidian. MCP and CLI share the same socket.

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

## CLI orphans / unresolved / backlinks cache lag — `eval` for truth

`obsidian orphans` / `unresolved` / `backlinks` read Obsidian's index, which **lags writes 1-5s** (longer on big vaults). Symptom: a note shows as resolved AND unresolved at once, or a freshly created note still appears as orphan, or alias/hub changes don't surface even after edits. Real incident 2026-05-26: CLI `unresolved` kept listing hubs as broken while `metadataCache` already resolved them.

**Authoritative check — `obsidian eval` on `metadataCache`:**

```bash
# Top broken (unresolved) targets — candidates for missing hub notes:
obsidian eval code="(()=>{const u=app.metadataCache.unresolvedLinks;const f={};Object.values(u).forEach(l=>Object.keys(l).forEach(t=>f[t]=(f[t]||0)+1));return JSON.stringify(Object.entries(f).sort((a,b)=>b[1]-a[1]).slice(0,10));})()" vault="main"

# Real backlink count for one note (does [[X]] actually resolve to it?):
obsidian eval code="(()=>{let n=0;for(const f of app.vault.getMarkdownFiles()){const rl=app.metadataCache.resolvedLinks[f.path]||{};for(const k in rl)if(k.endsWith('TARGET.md'))n++;}return n;})()" vault="main"
```

Treat CLI graph counts as **advisory** if notes were created/edited in the same session. `vault-health` and `session-review` should prefer `eval` for critical resolution checks.

## Forbidden chars in note names (`#` `.` `/`)

`#` breaks wikilinks (parsed as a heading anchor → permanent orphan, even existing links to it), `.` truncates CLI `create` at the dot, `/` makes a subfolder. Full table + the hub-note fix → `references/tool-routing.md` ("Note naming rules" + "Hub notes"). Always sanitize a name before `create`. Incident 2026-05-26: 56 `#`-named notes were silent orphans.

# Testing — claude-mnemo v0.7.3 smoke test

Pre-release smoke tests for v0.7.3. Run once after `/plugin update mnemo` to verify all 8 skills behave as intended after the v0.6.0 → v0.7.3 refactor.

## What changed in v0.7.3

Model routing was rewritten to prevent mid-session model switches from triggering `API Error: Extra usage is required for 1M context` on Max plans. Four skills now run in isolated forked subagents (`context: fork` + `haiku` or `sonnet`); the remaining four inherit the session model (`model: inherit`). See [CHANGELOG](./CHANGELOG.md#073---2026-04-24).

**Universal red flag for every test below:** if you see `API Error: Extra usage is required for 1M context` during any skill invocation, the routing regressed — a skill is still forcing a model switch in the main session. File an issue with the skill name.



## Prerequisites

- **Obsidian running**, vault `main` (or whatever is in `~/.mnemo/config.json`)
- **Plugin updated to v0.7.3** in the current session:
  ```
  /plugin update mnemo
  ```
  Verify:
  ```bash
  ls ~/.claude/plugins/cache/claude-mnemo/mnemo/
  # expected: 0.7.2 (plus maybe 0.6.1 legacy — that one can be deleted once confirmed working)
  ```
- **claude-mem plugin installed** (for Step 0 of `/mn:health` — the sanity check)

## Test plan — 7 checks, ~10 minutes total

### 1. `/mn:health` — the biggest surface

```
/mn:health
```

**Expect:**
- **Step 0 surfaces claude-mem state** — either "claude-mem v12.3.9, clean" (good) or a warning about stale cache / major-version skew.
- **Steps 1-4 execute in parallel** (you'll see 4 Bash tool calls in a single assistant message).
- **Step 5 is instant** (~50ms) — uses `grep -rL` against vault filesystem, not per-file `obsidian read`.
- Final report shows: vault size, note counts by type, orphans, missing `## Связи`, stale notes, top hubs.

**Red flags:**
- Step 5 takes >5 seconds → `get-vault-path.sh` failed or vault filesystem scan is slow
- "claude-mem" section missing even though the plugin is installed → `check-cm-version.sh` path resolution broken
- References to "Obsidian must be open" gotcha inline in the skill body → reference files didn't extract (shouldn't happen since linter passed, but verify)

### 2. `/mn:ask` — pushy description triggers

Try a recall-style query you know is in your vault:

```
/mn:ask "что мы решили про tiered models в mnemo"
```

**Expect:**
- Skill triggers (pushy description changes in v0.7.1 should make this reliable).
- Step 3 fires **multiple `obsidian search` calls in parallel** (one message, many tools).
- Step 4 reads up to 7 notes **in parallel**.
- Answer cites specific notes with source labels like `[Source: Session — X]`.

**Red flag:** skill runs searches sequentially (one at a time) → parallelism rule didn't land.

### 3. `/mn:connect` — single-grep performance

```
/mn:connect "Atom — mnemo ask стоит расширить knowledge-agent для глобальных вопросов"
```

**Expect:**
- Step 3 runs **one `grep -rlE` with all concepts OR'd** against `$(obsidian vault vault="main" | awk '/^path/{print $2}')` — not N separate `obsidian search` calls.
- Backlinks check runs in parallel with grep (two tool calls, one message).
- Total time ~1-2 seconds for 7 concepts.
- Output: ranked list of 5-7 candidate notes with "why relevant" blurbs. Does NOT auto-apply.

**Red flag:** you see 7 separate `obsidian search` calls → single-grep fix didn't land.

### 4. `/mn:save` — claude-mem metadata enrichment

```
/mn:save "Тестовая заметка: smoke test mnemo v0.7.3. Facade ping."
```

**Expect:**
- Skill classifies the input (fact/insight/decision/gotcha).
- Creates Obsidian note via MCP (`mcp__obsidian__create`, not CLI).
- POSTs to claude-mem at `127.0.0.1:37777` with metadata including:
  - `claude_mem_version` (auto-detected: `12.3.9`)
  - `obsidian_note` (the note filename)
  - `obsidian_vault` (`main`)
- Final report shows `Backends: Obsidian ✅, claude-mem ✅, memory/ ⏭` (or similar).

**Verify metadata:** in a follow-up, search claude-mem for the test note and confirm the metadata fields are present.

**Red flag:** `claude_mem_version` is empty/missing → version detection broken.

### 5. `/mn:review` — prewarmed caches + progressive disclosure

```
/mn:review
```

**Expect:**
- **First run of the session is near-instant** (~3s) because `plugins/mnemo/hooks/prewarm.sh` warmed `session-scan` + `skills-discover` caches on SessionStart.
- Session classified (Implementation / Research / Debugging / etc).
- Step 4 runs explicit `cat` on `triggers-{type}.md` + `triggers-universal.md` — you should see these file contents in the bash output.
- Skill gap analysis references the cat'd matrix, not an inline table in the skill body.

**Red flag:** no `cat triggers-*.md` call visible → Step 4 fix didn't land.

### 6. `/mn:sort` — bulk mode

Prereq: at least one `Inbox — <something>` note in the vault. If none, create one:
```
/mn:save "тестовый inbox note"
```
then tag it as `inbox` manually or classify quickly to generate backlog.

Run:
```
/mn:sort
```

Try saying **"применить все"** / **"accept all"** when prompted.

**Expect:** skill skips per-note `[1-5]` prompts and applies suggested classification to every note, showing `3/7: Atom — X created` progress lines.

**Red flag:** skill still asks per-note despite bulk intent → bulk mode didn't land.

### 7. `/mn:setup` — idempotent handoff

```
/mn:setup
```

**Expect:** skill detects existing `~/.mnemo/config.json`, shows current values, asks whether to overwrite before rewriting. **Does NOT clobber** the existing `Meta — Session Handoff.md` — Step 6 checks and skips creation if it exists.

**Red flag:** handoff gets overwritten → idempotency fix didn't land.

## CI verification (Optional — in browser)

Open <https://github.com/jojoprison/claude-mnemo/actions>. Last run (on commit `5ddfb0c`) should show **Skill lint ✅ passed** on `plugins/**` files. No workflow should be red.

## If something breaks

1. Note **which skill** and **what output differed** from "Expect" above.
2. Check cache: `ls ~/.claude/plugins/cache/claude-mnemo/mnemo/` — if only `0.6.1` is there, the update didn't take effect. Try `/plugin update mnemo` again or restart Claude Code.
3. Check CI: if GitHub Actions is red, the linter found an issue.
4. Open a fresh session with the same failure, tag Claude: "smoke test failed on `/mn:X`, expected Y, got Z" — we'll debug from there.

## Cleanup after a clean run

- Delete the test inbox note (`обычный inbox flow через /mn:sort`)
- Optionally delete the "Facade ping" test atom via Obsidian
- Remove legacy cache:
  ```bash
  rm -rf ~/.claude/plugins/cache/claude-mnemo/mnemo/0.6.1
  ```
  (Only after confirming v0.7.3 works.)

## Expected total time

~10 minutes on a warm vault. All 7 checks independent — you can skip any that aren't relevant, but `/mn:health` and `/mn:ask` are the most important (cover the most surface).

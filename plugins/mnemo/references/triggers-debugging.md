# Trigger Matrix — Debugging sessions

Read this file when session-review classifies the current session as **Debugging** (error patterns, "fix" commits, investigation flow).

| Signal | Recommended skill | Priority |
|--------|------------------|----------|
| Root cause identified (save as gotcha) | mnemo:save | HIGH |
| Fix committed without regression tests | test-master | CRITICAL |
| Investigation log worth preserving | mnemo:session | MEDIUM |
| Similar bug solved before | mnemo:ask (before fixing, to recall prior solution) | MEDIUM |
| Fix touches known-fragile code | review, ce:review | HIGH |

Also check universal triggers in `triggers-universal.md`.

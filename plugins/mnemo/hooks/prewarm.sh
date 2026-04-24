#!/usr/bin/env bash
# Prewarm /mn:review caches so the first review in a session is instant.
# Runs async on SessionStart — must not block the session.

set -euo pipefail

PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
SCRIPTS_DIR="${PLUGIN_ROOT}/scripts"

# Fail silently — prewarm is best-effort, never blocks the session.
[ -d "$SCRIPTS_DIR" ] || exit 0

# Warm skills-discover cache (300s TTL) — always safe, no session id needed.
python3 "$SCRIPTS_DIR/skills-discover.py" >/dev/null 2>&1 &

# Warm session-scan cache only if CLAUDE_SESSION_ID is present.
if [ -n "${CLAUDE_SESSION_ID:-}" ]; then
  python3 "$SCRIPTS_DIR/session-scan.py" >/dev/null 2>&1 &
fi

# Detach background jobs so the hook returns immediately.
disown -a 2>/dev/null || true
exit 0

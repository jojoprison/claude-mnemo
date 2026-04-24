#!/usr/bin/env bash
# Inspect the installed claude-mem plugin cache.
#
# Outputs three lines:
#   version: <latest version folder, or empty>
#   stale:   <number of version folders minus 1 — >0 means restart Claude windows>
#   path:    <path to cache root, or empty if not installed>
#
# Exit code: 0 always (missing plugin is not an error — just empty output).

set -u

CACHE="$HOME/.claude/plugins/cache/thedotmack/claude-mem"

if [ ! -d "$CACHE" ]; then
  echo "version:"
  echo "stale: 0"
  echo "path:"
  exit 0
fi

VERSIONS=$(ls -1 "$CACHE" 2>/dev/null | sort -V)
COUNT=$(echo "$VERSIONS" | grep -c . || true)
LATEST=$(echo "$VERSIONS" | tail -1)
STALE=$((COUNT > 0 ? COUNT - 1 : 0))

echo "version: $LATEST"
echo "stale: $STALE"
echo "path: $CACHE"

#!/usr/bin/env bash
# Return the filesystem path of an Obsidian vault.
# Usage: get-vault-path.sh [vault-name]  (defaults to "main")
#
# Output: single line with the absolute path, or empty string if unavailable.
# Exit code: 0 on success (even if empty), 1 only on fatal error.

set -u

VAULT="${1:-main}"
obsidian vault vault="$VAULT" 2>/dev/null | awk '/^path\s/{print $2; exit}'

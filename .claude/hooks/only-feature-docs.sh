#!/usr/bin/env bash
# PreToolUse-Hook für den feature-analyst: Write nur unter docs/features/*.md erlauben.

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(jq -r '.tool_input.file_path // empty')

case "$file" in
  *..*) ;;  # Pfade mit ".." grundsätzlich ablehnen
  "$root"/docs/features/*.md | docs/features/*.md) exit 0 ;;
esac

echo "feature-analyst darf nur Specs unter docs/features/<slug>.md schreiben, nicht: $file" >&2
exit 2

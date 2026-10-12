#!/usr/bin/env bash
# PostToolUse-Hook (Edit|Write): formatiert die geänderte Datei mit dem Projekt-Formatter.
# Bewusst schnell: nur Formatter auf eine Datei, keine Tests, kein ESLint.
# Fehlt ein Tool (venv/node_modules nicht installiert), wird still übersprungen.

root="${CLAUDE_PROJECT_DIR:-$(pwd)}"
file=$(jq -r '.tool_input.file_path // empty')
[ -z "$file" ] || [ ! -f "$file" ] && exit 0

case "$file" in
  "$root"/backend/*.py)
    ruff="$root/backend/.venv/bin/ruff"
    [ -x "$ruff" ] || exit 0
    cd "$root/backend" || exit 0
    "$ruff" format --quiet "$file"
    # Nur Import-Sortierung fixen: ungenutzte Imports nicht entfernen, solange der Agent noch editiert
    "$ruff" check --select I --fix --quiet "$file" >/dev/null 2>&1
    ;;
  "$root"/frontend/node_modules/*) ;;
  "$root"/frontend/*.vue | "$root"/frontend/*.ts | "$root"/frontend/*.js | "$root"/frontend/*.css | "$root"/frontend/*.json)
    prettier="$root/frontend/node_modules/.bin/prettier"
    [ -x "$prettier" ] || exit 0
    cd "$root/frontend" || exit 0
    "$prettier" --write --log-level warn "$file"
    ;;
esac
exit 0

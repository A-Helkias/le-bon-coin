#!/usr/bin/env sh
# PostToolUse — formate automatiquement le fichier que Claude vient d'écrire.
# Reçoit sur stdin le JSON de l'appel d'outil ; en extrait tool_input.file_path.
# Ne bloque jamais : sort toujours en 0, même en cas d'échec de l'outil de format.

payload=$(cat)

# Extraction de file_path, puis conversion des séparateurs Windows échappés en JSON.
file=$(printf '%s' "$payload" \
  | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
  | sed 's|\\\\|/|g')

[ -z "$file" ] && exit 0
[ -f "$file" ] || exit 0

root=$(cd "$(dirname "$0")/../.." && pwd)

case "$file" in
  *.py)
    command -v uv >/dev/null 2>&1 || exit 0
    [ -d "$root/backend" ] || exit 0
    (cd "$root/backend" && uv run ruff format "$file" && uv run ruff check --fix "$file") >/dev/null 2>&1
    echo "ruff : $(basename "$file") formaté" >&2
    ;;
  *.ts|*.tsx|*.js|*.jsx|*.css|*.json)
    command -v npx >/dev/null 2>&1 || exit 0
    [ -d "$root/frontend" ] || exit 0
    (cd "$root/frontend" && npx --no-install prettier --write "$file") >/dev/null 2>&1
    echo "prettier : $(basename "$file") formaté" >&2
    ;;
esac

exit 0

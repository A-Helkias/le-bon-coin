#!/usr/bin/env sh
# PreToolUse (matcher Bash) — refuse les commandes destructrices sur la base.
# Code de sortie 2 = l'appel d'outil est bloqué et stderr est renvoyé à Claude,
# qui peut alors expliquer ou proposer autre chose. Tout autre code laisse passer.

payload=$(cat)

cmd=$(printf '%s' "$payload" \
  | sed -n 's/.*"command"[[:space:]]*:[[:space:]]*"\(.*\)"[[:space:]]*}.*/\1/p')

[ -z "$cmd" ] && exit 0

refuser() {
  echo "BLOQUÉ par le hook db-guard : $1" >&2
  echo "Commande refusée : $cmd" >&2
  echo "Si c'est réellement voulu, demande une validation explicite à l'utilisateur avant de réessayer." >&2
  exit 2
}

case "$cmd" in
  *"alembic downgrade"*)
    refuser "un downgrade Alembic peut détruire des données" ;;
  *"docker compose down -v"*|*"docker-compose down -v"*)
    refuser "l'option -v supprime le volume Postgres et donc toute la base" ;;
  *DROP\ TABLE*|*"drop table"*|*DROP\ DATABASE*|*"drop database"*)
    refuser "suppression de table ou de base" ;;
  *TRUNCATE*|*truncate*)
    refuser "TRUNCATE vide la table sans possibilité de retour" ;;
esac

exit 0

---
description: Lance toute la chaîne de qualité (format, lint, types, tests) sur le back et le front, et corrige jusqu'au vert
argument-hint: "[back|front] (optionnel — les deux par défaut)"
allowed-tools: Bash(cd:*), Bash(uv:*), Bash(npm:*), Bash(npx:*), Read, Edit, Glob, Grep
---

Portée demandée : $1 (si vide, traite le back **et** le front).

Exécute la chaîne complète, dans cet ordre, en t'arrêtant au premier échec pour le corriger avant de continuer.

**Backend** (`cd backend`)
1. `uv run ruff format .`
2. `uv run ruff check --fix .`
3. `uv run mypy app`
4. `uv run pytest -q`

**Frontend** (`cd frontend`)
1. `npx prettier --write src`
2. `npm run lint -- --fix`
3. `npx tsc -b`  (le `tsconfig.json` racine n'est qu'un fichier de références : `--noEmit` seul ne vérifie aucun fichier)
4. `npm run test -- --run`

Règles :
- Corrige les erreurs, ne les contourne pas. Interdiction d'ajouter `# type: ignore`, `eslint-disable`, `@ts-expect-error` ou de marquer un test `skip` pour faire passer la chaîne.
- Si un test échoue, lis le code testé avant de modifier quoi que ce soit : c'est peut-être le code qui est faux, pas le test.
- Si une correction touche à la logique métier plutôt qu'à la forme, arrête-toi et explique le problème au lieu de décider seul.

Termine par un tableau récapitulatif : étape / statut / ce qui a été corrigé.

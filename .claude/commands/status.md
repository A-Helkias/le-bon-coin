---
description: Synthèse exhaustive de tous travaux effectués au cours de cette session pour reprise ultérieure par une autre instance claude.
allowed-tools: Bash(git:*), Bash(cd:*), Bash(uv:*), Bash(npm:*), Read, Glob, Grep
---

Établis un état des lieux factuel du projet Le Bon Coin. N'invente rien : chaque affirmation doit venir d'une lecture de fichier ou d'une commande.

1. **Périmètre livré** — parcours `backend/app/api/` et `frontend/src/features/` et liste les fonctionnalités réellement implémentées.
2. **Confrontation à l'objectif** — compare avec la liste cible : consultation des produits, détail produit, panier, commande, back-office, persistance, API.
3. **Santé technique** — lance les tests back et front, rapporte les compteurs réels (passés / échoués / ignorés).
4. **Dette visible** — `TODO`, `FIXME`, tests `skip`, routes sans test.
5. **Git** — branche courante, nombre de commits, fichiers non commités.

Rends un tableau `Fonctionnalité | État (✅ / 🚧 / ❌) | Preuve (fichier ou commande)`, suivi des **trois prochaines actions** classées par priorité, avec une justification d'une ligne chacune.

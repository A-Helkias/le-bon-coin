# Règle — méthode de travail

## Avant d'écrire du code

Pour toute tâche qui touche plus de deux fichiers, présente un plan et attends sa validation. Un plan corrigé coûte trente secondes ; un diff de trois cents lignes à défaire coûte vingt minutes.

## Pendant

- Lis le code existant avant de le modifier. Ne suppose pas une signature : va la vérifier.
- Suis les recettes des skills du projet (`api-entity`, `frontend-design`) plutôt que d'improviser une structure.
- N'ajoute pas de dépendance sans le signaler et justifier pourquoi la bibliothèque standard ou l'existant ne suffisent pas.
- Ne commente pas ce que le code dit déjà. Un commentaire explique un **pourquoi**, jamais un **quoi**.
- Ne crée pas de fichier de documentation spontanément. On documente quand c'est demandé.

## Avant de considérer une tâche terminée

1. `/check` passe au vert — format, lint, types, tests.
2. Les nouveaux comportements sont couverts par des tests, cas d'erreur compris.
3. `/review` (agent `code-reviewer`) ne remonte aucun constat bloquant.

Une tâche n'est pas terminée parce que le code est écrit. Elle est terminée quand elle est vérifiée.

## Git

- Une branche par fonctionnalité, nommée en anglais : `feat/product-catalog`, `fix/cart-total`.
- Jamais de commit direct sur `main`.
- Messages de commit au format Conventional Commits, `type(scope): description`, la description en français à l'impératif : « feat(api): ajoute le endpoint de détail produit ». Les types et scopes admis sont listés dans `.claude/agents/gitops.md`, et la liste est fermée.
- Ne commite et ne pousse que si on te le demande explicitement.

## Honnêteté du rapport

Si les tests échouent, dis-le et montre la sortie. Si une partie de la demande n'a pas été traitée, dis laquelle et pourquoi. Ne présente jamais comme vérifié ce qui ne l'a pas été.

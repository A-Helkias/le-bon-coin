---
description: Fait relire le diff courant par l'agent code-reviewer selon la grille du projet
argument-hint: "[branche ou fichier] (optionnel — le diff non commité par défaut)"
allowed-tools: Bash(git:*), Read, Glob, Grep, Agent
---

Périmètre : $ARGUMENTS (si vide, le diff non commité).

Lance l'agent **`code-reviewer`** sur ce périmètre et restitue son rapport tel quel, sans l'adoucir.

Ensuite seulement, et uniquement si des constats **Bloquant** ou **À corriger** remontent, propose un plan de correction — une ligne par constat. Ne corrige rien tant que ce plan n'est pas validé.

Si le rapport est vide, dis-le en une ligne et arrête-toi.

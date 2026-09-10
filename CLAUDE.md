# Le Bon Coin

Boutique de vente en ligne. Monorepo : `backend/` (FastAPI), `frontend/` (React), `docker/`, `iac/`, `docs/`, `.github/`.

## Stack

| Couche | Technologie |
|---|---|
| Frontend | React 19 + TypeScript + Vite + TanStack Query + Tailwind 4 |
| Backend | Python 3.12 + FastAPI + SQLAlchemy 2.0 (async) + Pydantic v2 |
| Base | PostgreSQL 16, migrations Alembic |
| Tests | pytest + httpx (back), Vitest + Testing Library (front) |
| Qualité | ruff + mypy strict (back), ESLint + Prettier (front) |
| Infra | Docker Compose, GitHub Actions |

## Commandes

```bash
docker compose up -d db                     # PostgreSQL local

cd backend
uv sync                                     # dépendances
uv run alembic upgrade head                 # migrations
uv run uvicorn app.main:app --reload        # API sur :8000
uv run pytest                               # tests

cd frontend
npm install
npm run dev                                 # interface sur :5173
npm run test
```

## Règles du projet

@.claude/rules/naming-and-language.md
@.claude/rules/backend.md
@.claude/rules/frontend.md
@.claude/rules/workflow.md

## Outillage disponible

| Type | Nom | Usage |
|---|---|---|
| Command | `/check [back\|front]` | chaîne de qualité complète, corrigée jusqu'au vert |
| Command | `/migrate <description>` | migration Alembic générée, relue, appliquée |
| Command | `/review` | relecture du diff par l'agent `code-reviewer` |
| Command | `/status` | état factuel du projet |
| Skill | `api-entity` | recette d'une entité backend sur les cinq couches |
| Skill | `python-pro` | qualité du Python — typage, async, pytest, mypy strict |
| Skill | `frontend-design` | recette d'un écran React — direction artistique, structure, hooks, tests |
| Agent | `api-explorer` | cartographie le backend en lecture seule |
| Agent | `code-reviewer` | relecture selon la grille du projet |
| Agent | `gitops` | découpe le travail en commits atomiques |

## Interdits

- `alembic downgrade`, `DROP`, `TRUNCATE`, `docker compose down -v` — bloqués par un hook.
- `requirements.txt` — le projet utilise `uv` et `pyproject.toml`.
- Commit direct sur `main`.

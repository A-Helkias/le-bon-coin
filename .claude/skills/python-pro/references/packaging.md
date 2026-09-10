# Python Packaging and Project Setup

> Rewritten for Le Bon Coin. The upstream version of this file documented Poetry,
> `pip install -e`, `setup.py` and `requirements.txt` — none of which this project uses.
> Dependency management here is `uv` + `pyproject.toml`, and `requirements.txt` is a
> hard prohibition (see `CLAUDE.md`). Formatting is `ruff format`, not `black`.

## Project Structure

The backend is an application, not a distributable library: no `src/` layout, no
build backend, no PyPI publication. The package lives at `backend/app/` and the
layers are the ones fixed by `.claude/rules/backend.md`.

```
backend/
├── pyproject.toml           # Project metadata, dependencies, tool config
├── uv.lock                  # Resolved dependency lockfile — committed
├── .python-version          # 3.12
├── alembic.ini              # Migration configuration
├── alembic/
│   └── versions/            # Migration scripts
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, global exception handlers
│   ├── api/                 # FastAPI routers — HTTP only
│   ├── services/            # Business logic — no HTTP, no SQLAlchemy
│   ├── repositories/        # Data access — the only layer importing SQLAlchemy
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   └── core/                # Config, security, exceptions, shared dependencies
└── tests/
    ├── conftest.py          # Async fixtures, disposable PostgreSQL database
    ├── api/
    ├── services/
    └── repositories/
```

## pyproject.toml

```toml
[project]
name = "le-bon-coin-backend"
version = "0.1.0"
description = "API de la boutique Le Bon Coin"
requires-python = ">=3.12,<3.13"

dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.32.0",
    "sqlalchemy[asyncio]>=2.0.36",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pydantic>=2.10.0",
    "pydantic-settings>=2.6.0",
]

[dependency-groups]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=6.0.0",
    "httpx>=0.28.0",
    "mypy>=1.13.0",
    "ruff>=0.8.0",
]

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "B",      # flake8-bugbear
    "C4",     # flake8-comprehensions
    "UP",     # pyupgrade
    "ASYNC",  # flake8-async — catches blocking calls inside async code
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"alembic/versions/*" = ["E501"]

[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
minversion = "8.0"
asyncio_mode = "auto"
# Tests and fixtures must share one event loop: the session-scoped engine holds
# asyncpg connections that cannot be handed to a different loop.
asyncio_default_fixture_loop_scope = "session"
asyncio_default_test_loop_scope = "session"
addopts = [
    "-ra",
    "--strict-markers",
    "--strict-config",
]
testpaths = ["tests"]

[tool.coverage.run]
source = ["app"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
]
```

There is no `[build-system]` table: the application is never built as a wheel.
Adding one invites `pip install -e .`, which is not how this project is run.

## uv Commands

```bash
uv sync                       # Install every dependency from uv.lock
uv sync --no-dev              # Production install, dev group excluded
uv lock                       # Re-resolve after editing pyproject.toml by hand
uv lock --upgrade             # Re-resolve to the newest allowed versions

uv add asyncpg                # Add a runtime dependency
uv add --dev pytest-asyncio   # Add a dev dependency
uv remove asyncpg             # Drop a dependency

uv run pytest                 # Run a command inside the project environment
uv run uvicorn app.main:app --reload
uv run alembic upgrade head
uv run ruff format .
uv run ruff check --fix .
uv run mypy app
```

`uv add` edits `pyproject.toml` and refreshes `uv.lock` in one step — never hand-edit
the lockfile, and never add a dependency without flagging and justifying it, per
`.claude/rules/workflow.md`.

## Virtual Environments

`uv` creates and manages `backend/.venv` on its own. There is nothing to activate:
`uv run <command>` executes inside it. Do not call `python -m venv`, `virtualenv`,
`pyenv` or `pip install` directly — they desynchronise the environment from the lockfile.

The interpreter version is pinned by `.python-version`:

```bash
echo "3.12" > .python-version
uv python install 3.12        # uv fetches the interpreter if it is missing
```

## Lockfile

`uv.lock` is committed. It pins exact versions and hashes for every platform, so
`uv sync` reproduces an identical environment in CI, in Docker and on a laptop.

A `requirements.txt` is never generated, not even as an export: `CLAUDE.md` lists it
among the project prohibitions. Docker images install from the lockfile.

## Configuration, Never Hardcoded Secrets

Settings come from the environment through `pydantic-settings`, in `app/core/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from the environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    debug: bool = False
```

`.env` is git-ignored and denied to Claude by `.claude/settings.json`. No credential is
ever written into `pyproject.toml`, a migration, or a test fixture.

## Docker

```dockerfile
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies are installed before the source is copied so the layer survives
# ordinary code changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

`--frozen` fails the build when `uv.lock` is out of date with `pyproject.toml`, which
turns a forgotten `uv lock` into a build error rather than a runtime surprise.

## CI/CD Integration

```yaml
# .github/workflows/backend.yml
name: Backend

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: le_bon_coin_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true

      - name: Install dependencies
        working-directory: backend
        run: uv sync --frozen

      - name: Format
        working-directory: backend
        run: uv run ruff format --check .

      - name: Lint
        working-directory: backend
        run: uv run ruff check .

      - name: Type check
        working-directory: backend
        run: uv run mypy app

      - name: Test
        working-directory: backend
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/le_bon_coin_test
        run: uv run pytest
```

Tests run against a real PostgreSQL 16 service, never SQLite: the constraints
exercised must be the constraints that ship.

## The Quality Chain

The four steps above — format, lint, types, tests — are exactly what `/check back`
runs locally. Run it before considering a task finished; it is the same chain CI runs,
so a green `/check` means a green pipeline.

Failing steps are fixed, never silenced. A `# type: ignore`, a `pytest.skip`, or a
loosened `ruff`/`mypy` setting added to make the chain pass is a rule violation, not
a fix.

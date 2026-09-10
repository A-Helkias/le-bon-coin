---
name: python-pro
description: Expertise Python 3.12 pour le backend du Bon Coin — typage complet, async de bout en bout, mypy strict, pytest, gestion d'erreurs. À utiliser pour écrire ou corriger du code Python : annotations de types, patterns async/await, protocoles, gestionnaires de contexte, fixtures pytest, configuration de ruff et mypy, et quand `/check back` échoue sur des erreurs de types ou de lint. Complète le skill api-entity, qui traite la structure en cinq couches d'une entité ; celui-ci traite la qualité du Python lui-même.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.1.0"
  domain: language
  triggers: Python development, type hints, async Python, pytest, mypy, dataclasses, Python best practices, Pythonic code
  role: specialist
  scope: implementation
  output-format: code
  related-skills: api-entity
  source: Jeffallan/claude-skills — skills/python-pro
  modifications: description traduite et adaptée au projet ; references/packaging.md réécrit pour uv ; section « Contraintes Le Bon Coin » ajoutée en fin de fichier
---

# Python Pro

Modern Python 3.11+ specialist focused on type-safe, async-first, production-ready code.

## When to Use This Skill

- Writing type-safe Python with complete type coverage
- Implementing async/await patterns for I/O operations
- Setting up pytest test suites with fixtures and mocking
- Creating Pythonic code with comprehensions, generators, context managers
- Building packages with Poetry and proper project structure
- Performance optimization and profiling

## Core Workflow

1. **Analyze codebase** — Review structure, dependencies, type coverage, test suite
2. **Design interfaces** — Define protocols, dataclasses, type aliases
3. **Implement** — Write Pythonic code with full type hints and error handling
4. **Test** — Create comprehensive pytest suite with >90% coverage
5. **Validate** — Run `mypy --strict`, `black`, `ruff`
   - If mypy fails: fix type errors reported and re-run before proceeding
   - If tests fail: debug assertions, update fixtures, and iterate until green
   - If ruff/black reports issues: apply auto-fixes, then re-validate

## Reference Guide

Load detailed guidance based on context:

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Type System | `references/type-system.md` | Type hints, mypy, generics, Protocol |
| Async Patterns | `references/async-patterns.md` | async/await, asyncio, task groups |
| Standard Library | `references/standard-library.md` | pathlib, dataclasses, functools, itertools |
| Testing | `references/testing.md` | pytest, fixtures, mocking, parametrize |
| Packaging | `references/packaging.md` | uv, pyproject.toml, Docker, CI — réécrit pour ce projet, ne parle pas de Poetry |

## Constraints

### MUST DO
- Type hints for all function signatures and class attributes
- PEP 8 compliance with black formatting
- Comprehensive docstrings (Google style)
- Test coverage exceeding 90% with pytest
- Use `X | None` instead of `Optional[X]` (Python 3.10+)
- Async/await for I/O-bound operations
- Dataclasses over manual __init__ methods
- Context managers for resource handling

### MUST NOT DO
- Skip type annotations on public APIs
- Use mutable default arguments
- Mix sync and async code improperly
- Ignore mypy errors in strict mode
- Use bare except clauses
- Hardcode secrets or configuration
- Use deprecated stdlib modules (use pathlib not os.path)

## Code Examples

### Type-annotated function with error handling
```python
from pathlib import Path

def read_config(path: Path) -> dict[str, str]:
    """Read configuration from a file.

    Args:
        path: Path to the configuration file.

    Returns:
        Parsed key-value configuration entries.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If a line cannot be parsed.
    """
    config: dict[str, str] = {}
    with path.open() as f:
        for line in f:
            key, _, value = line.partition("=")
            if not key.strip():
                raise ValueError(f"Invalid config line: {line!r}")
            config[key.strip()] = value.strip()
    return config
```

### Dataclass with validation
```python
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    host: str
    port: int
    debug: bool = False
    allowed_origins: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid port: {self.port}")
```

### Async pattern
```python
import asyncio
import httpx

async def fetch_all(urls: list[str]) -> list[bytes]:
    """Fetch multiple URLs concurrently."""
    async with httpx.AsyncClient() as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.content for r in responses]
```

### pytest fixture and parametrize
```python
import pytest
from pathlib import Path

@pytest.fixture
def config_file(tmp_path: Path) -> Path:
    cfg = tmp_path / "config.txt"
    cfg.write_text("host=localhost\nport=8080\n")
    return cfg

@pytest.mark.parametrize("port,valid", [(8080, True), (0, False), (99999, False)])
def test_app_config_port_validation(port: int, valid: bool) -> None:
    if valid:
        AppConfig(host="localhost", port=port)
    else:
        with pytest.raises(ValueError):
            AppConfig(host="localhost", port=port)
```

### mypy strict configuration (pyproject.toml)
```toml
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

Clean `mypy --strict` output looks like:
```
Success: no issues found in 12 source files
```
Any reported error (e.g., `error: Function is missing a return type annotation`) must be resolved before the implementation is considered complete.

## Output Templates

When implementing Python features, provide:
1. Module file with complete type hints
2. Test file with pytest fixtures
3. Type checking confirmation (mypy --strict passes)
4. Brief explanation of Pythonic patterns used

## Knowledge Reference

Python 3.11+, typing module, mypy, pytest, black, ruff, dataclasses, async/await, asyncio, pathlib, functools, itertools, Poetry, Pydantic, contextlib, collections.abc, Protocol

[Documentation](https://jeffallan.github.io/claude-skills/skills/language/python-pro/)


---

## Contraintes Le Bon Coin

*Section ajoutée au skill d'origine. Ce qui suit prime sur le corps du skill et sur les fichiers de `references/` chaque fois que les deux divergent.*

### Ce que le skill dit et que le projet contredit

| Le skill amont | Ici |
|---|---|
| Poetry, `pip install -e`, `requirements.txt` | `uv` et `pyproject.toml`. `requirements.txt` est un interdit du projet. |
| `black` pour le format | `ruff format`. N'installe pas `black` — voir `.claude/rules/workflow.md` sur les nouvelles dépendances. |
| Python 3.11+ | Python 3.12. `target-version = "py312"`, `python_version = "3.12"`. |
| « Dataclasses over manual `__init__` » | Les contrats d'API sont des schémas **Pydantic v2**, les tables des modèles **SQLAlchemy 2.0**. Une dataclass ne se justifie que pour un objet interne à un service, jamais pour ce qui entre ou sort d'une route. |
| « >90% coverage » | Le projet n'impose pas de seuil chiffré. Il impose autre chose, de plus contraignant : **chaque route a un test du cas nominal et d'au moins un cas d'erreur** (404, 409, 422). |
| `references/testing.md` : fixture paramétrée sur `sqlite`, chapitre `unittest.mock` | Les tests tournent sur une **vraie base PostgreSQL jetable**. Interdiction de mocker le repository dans un test d'API : on teste la chaîne complète. Le mock reste légitime pour isoler un service d'un appel réseau tiers. |

Les références `type-system.md`, `async-patterns.md` et `standard-library.md` sont reprises telles quelles et s'appliquent sans réserve.

### Le typage

`mypy --strict` est la règle du projet, pas une option de ce skill. Et surtout : **on ne fait jamais passer la chaîne avec un `# type: ignore`, un `skip` ou un assouplissement de la configuration**. Une erreur de types signale un vrai problème de conception — c'est le code qu'on corrige, pas le vérificateur qu'on fait taire.

`X | None` plutôt que `Optional[X]`, `list[str]` plutôt que `List[str]` : le skill a raison, et Python 3.12 rend ces formes obligatoires par cohérence.

### L'async

Le backend est asynchrone de bout en bout : `async def`, `AsyncSession`, `asyncpg`, `httpx.AsyncClient` dans les tests. Aucun driver synchrone, nulle part. La règle `ASYNC` de ruff est activée pour attraper les appels bloquants glissés dans une coroutine.

Attention à un piège que `references/async-patterns.md` n'aborde pas : `asyncio.gather` sur des requêtes partageant la **même** `AsyncSession` corrompt la session. Une session SQLAlchemy n'est pas concurrente. Pour paralléliser des accès base, il faut des sessions distinctes.

### Les couches

Ce skill sait écrire du bon Python, mais il ne connaît pas le découpage du projet. Il ne décide pas où le code va vivre — `.claude/rules/backend.md` et le skill `api-entity` le décident :

- Une requête SQLAlchemy n'existe que dans un repository.
- Un service n'importe jamais `fastapi` et ne lève jamais `HTTPException` — il lève une exception métier de `app/core/exceptions.py`.
- Un repository fait `flush()`, jamais `commit()`.
- Une route retourne un schéma Pydantic, jamais un modèle SQLAlchemy.

Un code parfaitement typé rangé dans la mauvaise couche reste à refaire.

### Les montants

Tout montant financier est un `int` en centimes : `price_cents: int`. Jamais de `float`, jamais de `Decimal` exposé dans un schéma d'API. Les exemples du skill amont qui manipulent des prix en flottants sont à transposer.

### Les docstrings

Le skill demande des docstrings Google style : d'accord. En **anglais**, comme tout ce que lit une machine, avec les libellés destinés à l'utilisateur en français à l'intérieur des exceptions métier :

```python
raise InsufficientStockError("Ce produit n'est plus disponible en quantité suffisante.")
```

Et la règle du projet sur les commentaires tient : un commentaire explique un **pourquoi**, jamais un **quoi**. Une docstring qui paraphrase la signature est du bruit.

### La validation

Le « Core Workflow » du skill se termine par `mypy --strict`, `black`, `ruff`. Ici cette étape porte un nom : **`/check back`**, qui enchaîne `ruff format`, `ruff check`, `mypy` et `pytest` et corrige jusqu'au vert. C'est la commande à lancer, et une tâche n'est pas terminée avant qu'elle passe.

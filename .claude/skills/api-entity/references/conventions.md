# Conventions détaillées — backend Le Bon Coin

## Signatures de repository

```python
async def get(db: AsyncSession, product_id: UUID) -> Product | None
async def get_by_sku(db: AsyncSession, sku: str) -> Product | None
async def list_all(db: AsyncSession, *, limit: int = 50, offset: int = 0) -> Sequence[Product]
async def create(db: AsyncSession, data: ProductCreate) -> Product
async def update(db: AsyncSession, product: Product, data: ProductUpdate) -> Product
async def delete(db: AsyncSession, product: Product) -> None
```

Le repository fait `await db.flush()` pour obtenir les valeurs générées, **jamais** `await db.commit()` : le commit appartient à la dépendance de session.

## Exceptions métier — `app/core/exceptions.py`

| Exception | Traduction HTTP |
|---|---|
| `NotFoundError` | 404 |
| `AlreadyExistsError` | 409 |
| `BusinessRuleError` | 422 |
| `InsufficientStockError` | 409 |

Elles sont traduites par un `exception_handler` global déclaré dans `app/main.py`. Un routeur ne lève donc jamais `HTTPException` lui-même.

## Dépendance de session

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

## Fixtures de test — `tests/conftest.py`

| Fixture | Fournit |
|---|---|
| `db_session` | `AsyncSession` sur une base jetable, rollback après chaque test |
| `client` | `httpx.AsyncClient` avec `get_db` surchargé vers `db_session` |
| `product_factory` | crée un produit persisté, champs surchargeables |

Chaque test est indépendant : aucun ne suppose l'état laissé par un autre.

## Pagination

Toute route de liste accepte `limit` (défaut 50, max 200) et `offset`, et retourne une enveloppe `{"items": [...], "total": int}`.

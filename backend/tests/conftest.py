import itertools
import os
from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import Any

import pytest
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from alembic import command
from app.core.database import get_db
from app.main import app
from app.models import Product

ProductFactory = Callable[..., Awaitable[Product]]

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/le_bon_coin_test",
)


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
    """Bring the disposable database up to head once for the whole run."""
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(config, "head")


@pytest.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Session bound to a transaction that is rolled back, so tests stay independent."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = async_sessionmaker(bind=connection, expire_on_commit=False)()
        try:
            yield session
        finally:
            await session.close()
            # A constraint violation already rolled the transaction back; asking
            # again warns rather than helping.
            if transaction.is_active:
                await transaction.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """API client wired to the test session, exercising the real chain down to Postgres."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture
def product_factory(db_session: AsyncSession) -> ProductFactory:
    """Persist a product with sensible defaults; every field can be overridden.

    Each call gets a distinct SKU so a test can create several products without
    tripping the unique index.
    """
    counter = itertools.count(1)

    async def factory(**overrides: Any) -> Product:
        index = next(counter)
        fields: dict[str, Any] = {
            "sku": f"SKU-{index:04d}",
            "name": f"Produit {index}",
            "price_cents": 1999,
            "stock": 10,
            "is_active": True,
        }
        fields.update(overrides)
        product = Product(**fields)
        db_session.add(product)
        await db_session.flush()
        await db_session.refresh(product)
        return product

    return factory

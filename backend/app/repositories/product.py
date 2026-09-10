from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def get(db: AsyncSession, product_id: UUID) -> Product | None:
    return await db.get(Product, product_id)


async def get_by_sku(db: AsyncSession, sku: str) -> Product | None:
    result = await db.execute(select(Product).where(Product.sku == sku))
    return result.scalar_one_or_none()


async def get_many_for_update(db: AsyncSession, product_ids: Sequence[UUID]) -> list[Product]:
    """Load products and hold a row lock until the transaction ends.

    Args:
        db: Active session.
        product_ids: Products to lock.

    Returns:
        The matching products, in an unspecified order.

    Two concurrent checkouts on the last unit would otherwise both pass the
    stock check and drive the count below zero.
    """
    result = await db.execute(select(Product).where(Product.id.in_(product_ids)).with_for_update())
    return list(result.scalars().all())


async def list_all(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
    include_inactive: bool = False,
) -> Sequence[Product]:
    query = select(Product).order_by(Product.created_at.desc(), Product.id)
    if not include_inactive:
        query = query.where(Product.is_active.is_(True))
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()


async def count(db: AsyncSession, *, include_inactive: bool = False) -> int:
    query = select(func.count()).select_from(Product)
    if not include_inactive:
        query = query.where(Product.is_active.is_(True))
    result = await db.execute(query)
    return result.scalar_one()


async def create(db: AsyncSession, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()
    return product


async def update(db: AsyncSession, product: Product, data: ProductUpdate) -> Product:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.flush()
    return product

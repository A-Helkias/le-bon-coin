from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Product
from app.schemas.product import ProductCreate, ProductSort, ProductUpdate


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


def _filtered[T: tuple[Any, ...]](
    query: Select[T],
    *,
    include_inactive: bool,
    search: str | None,
    category: str | None,
) -> Select[T]:
    """Apply the catalogue filters.

    `list_all` and `count` must apply exactly the same conditions, otherwise the
    `total` of a paginated response describes a different set than its `items`.
    """
    if not include_inactive:
        query = query.where(Product.is_active.is_(True))
    if search:
        pattern = f"%{search}%"
        query = query.where(or_(Product.name.ilike(pattern), Product.sku.ilike(pattern)))
    if category:
        query = query.where(Product.category == category)
    return query


_ORDERINGS: dict[ProductSort, tuple[Any, ...]] = {
    ProductSort.PRICE_ASC: (Product.price_cents.asc(), Product.id),
    ProductSort.PRICE_DESC: (Product.price_cents.desc(), Product.id),
    ProductSort.RECENT: (Product.created_at.desc(), Product.id),
}


async def list_all(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
    include_inactive: bool = False,
    search: str | None = None,
    category: str | None = None,
    sort: ProductSort = ProductSort.RECENT,
) -> Sequence[Product]:
    query = _filtered(
        select(Product),
        include_inactive=include_inactive,
        search=search,
        category=category,
    ).order_by(*_ORDERINGS[sort])
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()


async def count(
    db: AsyncSession,
    *,
    include_inactive: bool = False,
    search: str | None = None,
    category: str | None = None,
) -> int:
    query = _filtered(
        select(func.count()).select_from(Product),
        include_inactive=include_inactive,
        search=search,
        category=category,
    )
    result = await db.execute(query)
    return result.scalar_one()


async def list_categories(db: AsyncSession) -> Sequence[str]:
    """Distinct categories carried by products still on sale."""
    result = await db.execute(
        select(Product.category)
        .where(Product.is_active.is_(True), Product.category.is_not(None))
        .distinct()
        .order_by(Product.category)
    )
    return [category for category in result.scalars().all() if category is not None]


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

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Order, OrderItem, OrderStatus


async def get(db: AsyncSession, order_id: UUID) -> Order | None:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
        # Re-reading an order already in the identity map must show the lines
        # just inserted, not the collection state from earlier in the request.
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def list_all(
    db: AsyncSession,
    *,
    limit: int = 50,
    offset: int = 0,
    status: OrderStatus | None = None,
) -> Sequence[Order]:
    query = (
        select(Order).options(selectinload(Order.items)).order_by(Order.created_at.desc(), Order.id)
    )
    if status is not None:
        query = query.where(Order.status == status)
    result = await db.execute(query.limit(limit).offset(offset))
    return result.scalars().all()


async def count(db: AsyncSession, *, status: OrderStatus | None = None) -> int:
    query = select(func.count()).select_from(Order)
    if status is not None:
        query = query.where(Order.status == status)
    result = await db.execute(query)
    return result.scalar_one()


async def create(db: AsyncSession, order: Order, items: Sequence[OrderItem]) -> Order:
    """Persist an order and its lines, both already built by the service.

    Args:
        db: Active session.
        order: Order to insert.
        items: Lines to attach, carrying their frozen product snapshots.

    Returns:
        The persisted order. Its `items` collection is not loaded; callers
        that render it re-read through `get`.
    """
    db.add(order)
    await db.flush()
    for item in items:
        item.order_id = order.id
        db.add(item)
    await db.flush()
    return order


async def save(db: AsyncSession, order: Order) -> Order:
    await db.flush()
    return order

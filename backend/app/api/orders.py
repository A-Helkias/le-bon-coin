from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import PaginationDep
from app.core.database import get_db
from app.models import OrderStatus
from app.schemas.order import OrderCreate, OrderRead, OrderUpdate
from app.schemas.pagination import Page
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["commandes"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=Page[OrderRead])
async def list_orders(
    db: DbDep,
    pagination: PaginationDep,
    order_status: Annotated[OrderStatus | None, Query(alias="status")] = None,
) -> Page[OrderRead]:
    orders, total = await order_service.list_orders(
        db, limit=pagination.limit, offset=pagination.offset, status=order_status
    )
    return Page(items=[OrderRead.from_order(o) for o in orders], total=total)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(db: DbDep, order_id: UUID) -> OrderRead:
    order = await order_service.get_order(db, order_id)
    return OrderRead.from_order(order)


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def create_order(db: DbDep, data: OrderCreate) -> OrderRead:
    """Turn a cart into an order. The cart is consumed on success."""
    order = await order_service.create_order_from_cart(db, data)
    return OrderRead.from_order(order)


@router.patch("/{order_id}", response_model=OrderRead)
async def update_order_status(db: DbDep, order_id: UUID, data: OrderUpdate) -> OrderRead:
    order = await order_service.update_status(db, order_id, data.status)
    return OrderRead.from_order(order)

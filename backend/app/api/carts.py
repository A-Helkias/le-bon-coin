from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartRead
from app.services import cart as cart_service

router = APIRouter(prefix="/carts", tags=["paniers"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.post("", response_model=CartRead, status_code=status.HTTP_201_CREATED)
async def create_cart(db: DbDep) -> CartRead:
    cart = await cart_service.create_cart(db)
    return CartRead.from_cart(cart)


@router.get("/{cart_id}", response_model=CartRead)
async def get_cart(db: DbDep, cart_id: UUID) -> CartRead:
    cart = await cart_service.get_cart(db, cart_id)
    return CartRead.from_cart(cart)


@router.delete("/{cart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart(db: DbDep, cart_id: UUID) -> None:
    await cart_service.delete_cart(db, cart_id)


@router.post("/{cart_id}/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
async def add_item(db: DbDep, cart_id: UUID, data: CartItemCreate) -> CartRead:
    cart = await cart_service.add_item(db, cart_id, data.product_id, data.quantity)
    return CartRead.from_cart(cart)


@router.patch("/{cart_id}/items/{product_id}", response_model=CartRead)
async def set_item_quantity(
    db: DbDep, cart_id: UUID, product_id: UUID, data: CartItemUpdate
) -> CartRead:
    cart = await cart_service.set_item_quantity(db, cart_id, product_id, data.quantity)
    return CartRead.from_cart(cart)


@router.delete("/{cart_id}/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item(db: DbDep, cart_id: UUID, product_id: UUID) -> None:
    await cart_service.remove_item(db, cart_id, product_id)

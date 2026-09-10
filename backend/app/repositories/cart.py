from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Cart, CartItem, Product


async def get(db: AsyncSession, cart_id: UUID) -> Cart | None:
    """Load a cart with its lines and each line's product.

    Args:
        db: Active session.
        cart_id: Cart to load.

    Returns:
        The cart, or None. Relationships are eager-loaded because the models
        declare `lazy="raise"`.
    """
    result = await db.execute(
        select(Cart)
        .where(Cart.id == cart_id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
        # Without this, re-reading a cart already in the identity map keeps the
        # collection loaded earlier in the request and hides the line just added.
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def create(db: AsyncSession) -> Cart:
    """Insert an empty cart.

    The instance comes back without its `items` collection loaded — callers
    that need to render it re-read through `get`.
    """
    cart = Cart()
    db.add(cart)
    await db.flush()
    return cart


async def delete(db: AsyncSession, cart: Cart) -> None:
    await db.delete(cart)
    await db.flush()


async def get_item(db: AsyncSession, cart_id: UUID, product_id: UUID) -> CartItem | None:
    result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
    )
    return result.scalar_one_or_none()


async def add_item(db: AsyncSession, cart: Cart, product: Product, quantity: int) -> CartItem:
    item = CartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
    db.add(item)
    await db.flush()
    return item


async def set_item_quantity(db: AsyncSession, item: CartItem, quantity: int) -> CartItem:
    item.quantity = quantity
    await db.flush()
    return item


async def delete_item(db: AsyncSession, item: CartItem) -> None:
    await db.delete(item)
    await db.flush()

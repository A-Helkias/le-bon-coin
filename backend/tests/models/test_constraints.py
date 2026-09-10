"""The guarantees below are enforced by PostgreSQL, not by the application.

Each test asserts that the database itself refuses the bad state, which is why
the suite runs against a real PostgreSQL rather than an approximation.
"""

import pytest
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Cart, CartItem, Order, OrderItem, Product


def build_product(**overrides: object) -> Product:
    defaults: dict[str, object] = {
        "sku": "SKU-001",
        "name": "Chaise en chêne",
        "price_cents": 12900,
        "stock": 5,
    }
    return Product(**{**defaults, **overrides})


def build_order(**overrides: object) -> Order:
    defaults: dict[str, object] = {
        "total_cents": 12900,
        "customer_email": "client@example.com",
        "customer_name": "Camille Martin",
        "shipping_address": "12 rue des Lilas",
        "shipping_postal_code": "75011",
        "shipping_city": "Paris",
        "shipping_country": "FR",
    }
    return Order(**{**defaults, **overrides})


async def test_duplicate_sku_is_rejected(db_session: AsyncSession) -> None:
    db_session.add(build_product())
    await db_session.flush()

    db_session.add(build_product(name="Autre chaise"))

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_negative_price_is_rejected(db_session: AsyncSession) -> None:
    db_session.add(build_product(price_cents=-1))

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_zero_quantity_cart_item_is_rejected(db_session: AsyncSession) -> None:
    product = build_product()
    cart = Cart()
    db_session.add_all([product, cart])
    await db_session.flush()

    db_session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=0))

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_same_product_twice_in_a_cart_is_rejected(db_session: AsyncSession) -> None:
    product = build_product()
    cart = Cart()
    db_session.add_all([product, cart])
    await db_session.flush()

    db_session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=1))
    await db_session.flush()

    db_session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=2))

    with pytest.raises(IntegrityError):
        await db_session.flush()


async def test_deleting_a_cart_deletes_its_items(db_session: AsyncSession) -> None:
    product = build_product()
    cart = Cart()
    db_session.add_all([product, cart])
    await db_session.flush()

    db_session.add(CartItem(cart_id=cart.id, product_id=product.id, quantity=2))
    await db_session.flush()

    # Issued as SQL so the cascade is PostgreSQL's, not SQLAlchemy's.
    await db_session.execute(delete(Cart).where(Cart.id == cart.id))
    await db_session.flush()

    remaining = await db_session.execute(select(CartItem).where(CartItem.cart_id == cart.id))
    assert remaining.scalars().all() == []


async def test_deleting_an_ordered_product_is_rejected(db_session: AsyncSession) -> None:
    product = build_product()
    order = build_order()
    db_session.add_all([product, order])
    await db_session.flush()

    db_session.add(
        OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            unit_price_cents=product.price_cents,
            quantity=1,
        )
    )
    await db_session.flush()

    # RESTRICT fires on the DELETE statement itself, not on a later flush.
    with pytest.raises(IntegrityError):
        await db_session.execute(delete(Product).where(Product.id == product.id))


async def test_unknown_order_status_is_rejected(db_session: AsyncSession) -> None:
    db_session.add(build_order(status="refunded"))

    with pytest.raises(IntegrityError):
        await db_session.flush()

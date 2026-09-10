from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, InsufficientStockError, NotFoundError
from app.models import Order, OrderItem, OrderStatus, Product
from app.repositories import cart as cart_repo
from app.repositories import order as order_repo
from app.repositories import product as product_repo
from app.schemas.order import OrderCreate
from app.services.cart import get_cart

# Anything absent from this table is refused. `shipped` and `cancelled` are terminal.
ALLOWED_TRANSITIONS: dict[OrderStatus, frozenset[OrderStatus]] = {
    OrderStatus.PENDING: frozenset({OrderStatus.PAID, OrderStatus.CANCELLED}),
    OrderStatus.PAID: frozenset({OrderStatus.SHIPPED, OrderStatus.CANCELLED}),
    OrderStatus.SHIPPED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}


async def get_order(db: AsyncSession, order_id: UUID) -> Order:
    """Raises:
    NotFoundError: No order carries this id.
    """
    order = await order_repo.get(db, order_id)
    if order is None:
        raise NotFoundError("Cette commande n'existe pas.")
    return order


async def list_orders(
    db: AsyncSession,
    *,
    limit: int,
    offset: int,
    status: OrderStatus | None = None,
) -> tuple[Sequence[Order], int]:
    orders = await order_repo.list_all(db, limit=limit, offset=offset, status=status)
    total = await order_repo.count(db, status=status)
    return orders, total


async def create_order_from_cart(db: AsyncSession, data: OrderCreate) -> Order:
    """Turn a cart into an order, freezing prices and consuming stock.

    Everything happens in the caller's transaction: validation, snapshots,
    stock decrement and cart removal succeed together or not at all.

    Raises:
        NotFoundError: The cart does not exist.
        BusinessRuleError: The cart is empty, or a product left the catalogue.
        InsufficientStockError: A product no longer has the requested quantity.
    """
    cart = await get_cart(db, data.cart_id)
    if not cart.items:
        raise BusinessRuleError("Votre panier est vide.")

    wanted = {item.product_id: item.quantity for item in cart.items}
    # Locked for the rest of the transaction, so a concurrent checkout cannot
    # pass the same stock check and drive the count below zero.
    locked = await product_repo.get_many_for_update(db, list(wanted))
    products = {product.id: product for product in locked}

    items: list[OrderItem] = []
    total_cents = 0
    for product_id, quantity in wanted.items():
        product = products.get(product_id)
        if product is None:
            raise NotFoundError("Ce produit n'existe pas.")
        if not product.is_active:
            raise BusinessRuleError(f"« {product.name} » n'est plus disponible à la vente.")
        if quantity > product.stock:
            raise InsufficientStockError(
                f"« {product.name} » n'est plus disponible en quantité suffisante."
            )

        items.append(_freeze_line(product, quantity))
        total_cents += product.price_cents * quantity
        product.stock -= quantity

    order = Order(
        status=OrderStatus.PENDING,
        total_cents=total_cents,
        customer_email=str(data.customer_email),
        customer_name=data.customer_name,
        shipping_address=data.shipping_address,
        shipping_postal_code=data.shipping_postal_code,
        shipping_city=data.shipping_city,
        shipping_country=data.shipping_country,
    )
    await order_repo.create(db, order, items)
    await cart_repo.delete(db, cart)
    return await get_order(db, order.id)


def _freeze_line(product: Product, quantity: int) -> OrderItem:
    """Copy the catalogue values an order must keep regardless of later edits."""
    return OrderItem(
        product_id=product.id,
        product_name=product.name,
        product_sku=product.sku,
        unit_price_cents=product.price_cents,
        quantity=quantity,
    )


async def update_status(db: AsyncSession, order_id: UUID, status: OrderStatus) -> Order:
    """Move an order to a new status, returning stock when it is cancelled.

    Raises:
        NotFoundError: No order carries this id.
        BusinessRuleError: The transition is not allowed.
    """
    order = await get_order(db, order_id)

    if status not in ALLOWED_TRANSITIONS[order.status]:
        raise BusinessRuleError(
            f"Une commande « {order.status} » ne peut pas passer à « {status} »."
        )

    if status is OrderStatus.CANCELLED:
        await _restore_stock(db, order)

    order.status = status
    return await order_repo.save(db, order)


async def _restore_stock(db: AsyncSession, order: Order) -> None:
    locked = await product_repo.get_many_for_update(db, [item.product_id for item in order.items])
    products = {product.id: product for product in locked}
    for item in order.items:
        product = products.get(item.product_id)
        # RESTRICT guarantees the product still exists; the guard keeps mypy
        # honest about the dict lookup.
        if product is not None:
            product.stock += item.quantity

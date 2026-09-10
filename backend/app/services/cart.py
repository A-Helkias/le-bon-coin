from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BusinessRuleError, InsufficientStockError, NotFoundError
from app.models import Cart, Product
from app.repositories import cart as cart_repo
from app.repositories import product as product_repo


async def _get_available_product(db: AsyncSession, product_id: UUID) -> Product:
    product = await product_repo.get(db, product_id)
    if product is None:
        raise NotFoundError("Ce produit n'existe pas.")
    if not product.is_active:
        raise BusinessRuleError("Ce produit n'est plus disponible à la vente.")
    return product


def _ensure_stock(product: Product, wanted: int) -> None:
    if wanted > product.stock:
        raise InsufficientStockError("Ce produit n'est plus disponible en quantité suffisante.")


async def create_cart(db: AsyncSession) -> Cart:
    """Create an empty cart and return it fully loaded, ready to render."""
    created = await cart_repo.create(db)
    return await get_cart(db, created.id)


async def get_cart(db: AsyncSession, cart_id: UUID) -> Cart:
    """Fetch a cart with its lines.

    Raises:
        NotFoundError: No cart carries this id.
    """
    cart = await cart_repo.get(db, cart_id)
    if cart is None:
        raise NotFoundError("Ce panier n'existe pas.")
    return cart


async def delete_cart(db: AsyncSession, cart_id: UUID) -> None:
    """Raises:
    NotFoundError: No cart carries this id.
    """
    cart = await get_cart(db, cart_id)
    await cart_repo.delete(db, cart)


async def add_item(db: AsyncSession, cart_id: UUID, product_id: UUID, quantity: int) -> Cart:
    """Add a product to a cart, merging with an existing line.

    Adding a product that is already in the cart increases that line rather
    than failing on the unique constraint, and the stock check covers the
    resulting total, not just the added quantity.

    Raises:
        NotFoundError: The cart or the product does not exist.
        BusinessRuleError: The product is no longer on sale.
        InsufficientStockError: Not enough stock for the resulting quantity.
    """
    await get_cart(db, cart_id)
    product = await _get_available_product(db, product_id)

    existing = await cart_repo.get_item(db, cart_id, product_id)
    wanted = quantity if existing is None else existing.quantity + quantity
    _ensure_stock(product, wanted)

    if existing is None:
        cart = await get_cart(db, cart_id)
        await cart_repo.add_item(db, cart, product, quantity)
    else:
        await cart_repo.set_item_quantity(db, existing, wanted)

    return await get_cart(db, cart_id)


async def set_item_quantity(
    db: AsyncSession, cart_id: UUID, product_id: UUID, quantity: int
) -> Cart:
    """Set the exact quantity of one cart line.

    Raises:
        NotFoundError: The cart, the product, or the line does not exist.
        BusinessRuleError: The product is no longer on sale.
        InsufficientStockError: Not enough stock for the requested quantity.
    """
    await get_cart(db, cart_id)
    product = await _get_available_product(db, product_id)

    item = await cart_repo.get_item(db, cart_id, product_id)
    if item is None:
        raise NotFoundError("Ce produit n'est pas dans le panier.")

    _ensure_stock(product, quantity)
    await cart_repo.set_item_quantity(db, item, quantity)
    return await get_cart(db, cart_id)


async def remove_item(db: AsyncSession, cart_id: UUID, product_id: UUID) -> None:
    """Raises:
    NotFoundError: The cart does not exist, or the product is not in it.
    """
    await get_cart(db, cart_id)
    item = await cart_repo.get_item(db, cart_id, product_id)
    if item is None:
        raise NotFoundError("Ce produit n'est pas dans le panier.")
    await cart_repo.delete_item(db, item)

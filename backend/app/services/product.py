from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AlreadyExistsError, NotFoundError
from app.models import Product
from app.repositories import product as product_repo
from app.schemas.product import ProductCreate, ProductUpdate


async def get_product(db: AsyncSession, product_id: UUID) -> Product:
    """Fetch one product.

    Raises:
        NotFoundError: No product carries this id.
    """
    product = await product_repo.get(db, product_id)
    if product is None:
        raise NotFoundError("Ce produit n'existe pas.")
    return product


async def list_products(
    db: AsyncSession,
    *,
    limit: int,
    offset: int,
    include_inactive: bool = False,
) -> tuple[Sequence[Product], int]:
    products = await product_repo.list_all(
        db, limit=limit, offset=offset, include_inactive=include_inactive
    )
    total = await product_repo.count(db, include_inactive=include_inactive)
    return products, total


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    """Create a product.

    Raises:
        AlreadyExistsError: The SKU is already taken.
    """
    if await product_repo.get_by_sku(db, data.sku) is not None:
        raise AlreadyExistsError("Un produit porte déjà cette référence.")
    return await product_repo.create(db, data)


async def update_product(db: AsyncSession, product_id: UUID, data: ProductUpdate) -> Product:
    """Update a product.

    Raises:
        NotFoundError: No product carries this id.
        AlreadyExistsError: The new SKU belongs to another product.
    """
    product = await get_product(db, product_id)

    if data.sku is not None and data.sku != product.sku:
        existing = await product_repo.get_by_sku(db, data.sku)
        if existing is not None:
            raise AlreadyExistsError("Un produit porte déjà cette référence.")

    return await product_repo.update(db, product, data)


async def deactivate_product(db: AsyncSession, product_id: UUID) -> None:
    """Remove a product from the catalogue without deleting it.

    Past orders reference it forever, so the row must survive.

    Raises:
        NotFoundError: No product carries this id.
    """
    product = await get_product(db, product_id)
    await product_repo.update(db, product, ProductUpdate(is_active=False))

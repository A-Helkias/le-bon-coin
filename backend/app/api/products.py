from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import PaginationDep
from app.core.database import get_db
from app.schemas.pagination import Page
from app.schemas.product import ProductCreate, ProductRead, ProductSort, ProductUpdate
from app.services import product as product_service

router = APIRouter(prefix="/products", tags=["produits"])

DbDep = Annotated[AsyncSession, Depends(get_db)]


@router.get("", response_model=Page[ProductRead])
async def list_products(
    db: DbDep,
    pagination: PaginationDep,
    q: Annotated[str | None, Query(max_length=100)] = None,
    category: Annotated[str | None, Query(max_length=50)] = None,
    sort: Annotated[ProductSort, Query()] = ProductSort.RECENT,
    include_inactive: Annotated[bool, Query()] = False,
) -> Page[ProductRead]:
    products, total = await product_service.list_products(
        db,
        limit=pagination.limit,
        offset=pagination.offset,
        include_inactive=include_inactive,
        search=q,
        category=category,
        sort=sort,
    )
    return Page(items=[ProductRead.model_validate(p) for p in products], total=total)


# Declared before /{product_id}, otherwise FastAPI matches "categories" as a
# product id and answers 422 instead of listing the aisles.
@router.get("/categories", response_model=list[str])
async def list_categories(db: DbDep) -> list[str]:
    """The aisles the catalogue actually uses, so the interface never invents them."""
    return list(await product_service.list_categories(db))


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(db: DbDep, product_id: UUID) -> ProductRead:
    product = await product_service.get_product(db, product_id)
    return ProductRead.model_validate(product)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(db: DbDep, data: ProductCreate) -> ProductRead:
    product = await product_service.create_product(db, data)
    return ProductRead.model_validate(product)


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(db: DbDep, product_id: UUID, data: ProductUpdate) -> ProductRead:
    product = await product_service.update_product(db, product_id, data)
    return ProductRead.model_validate(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_product(db: DbDep, product_id: UUID) -> None:
    """Take the product off the catalogue. The row survives for past orders."""
    await product_service.deactivate_product(db, product_id)

from fastapi import APIRouter

from app.api import carts, orders, products

api_router = APIRouter()
api_router.include_router(products.router)
api_router.include_router(carts.router)
api_router.include_router(orders.router)

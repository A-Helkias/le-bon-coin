from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models import Order, OrderItem, OrderStatus


class OrderCreate(BaseModel):
    cart_id: UUID
    customer_email: EmailStr
    customer_name: str = Field(min_length=1, max_length=200)
    shipping_address: str = Field(min_length=1, max_length=255)
    shipping_postal_code: str = Field(min_length=1, max_length=16)
    shipping_city: str = Field(min_length=1, max_length=120)
    # ISO 3166-1 alpha-2, upper case.
    shipping_country: str = Field(pattern=r"^[A-Z]{2}$")


class OrderUpdate(BaseModel):
    status: OrderStatus


class OrderItemRead(BaseModel):
    product_id: UUID
    product_name: str
    product_sku: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int

    @classmethod
    def from_item(cls, item: OrderItem) -> Self:
        """Build a line from the values frozen at checkout, not from the product."""
        return cls(
            product_id=item.product_id,
            product_name=item.product_name,
            product_sku=item.product_sku,
            unit_price_cents=item.unit_price_cents,
            quantity=item.quantity,
            line_total_cents=item.unit_price_cents * item.quantity,
        )


class OrderRead(BaseModel):
    id: UUID
    user_id: UUID | None
    status: OrderStatus
    total_cents: int
    customer_email: str
    customer_name: str
    shipping_address: str
    shipping_postal_code: str
    shipping_city: str
    shipping_country: str
    items: list[OrderItemRead]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_order(cls, order: Order) -> Self:
        """Build the order view.

        Args:
            order: Order with `items` eagerly loaded.

        Returns:
            The order as it was recorded, unaffected by later catalogue changes.
        """
        return cls(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_cents=order.total_cents,
            customer_email=order.customer_email,
            customer_name=order.customer_name,
            shipping_address=order.shipping_address,
            shipping_postal_code=order.shipping_postal_code,
            shipping_city=order.shipping_city,
            shipping_country=order.shipping_country,
            items=[OrderItemRead.from_item(item) for item in order.items],
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

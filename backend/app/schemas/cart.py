from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, Field

from app.models import Cart, CartItem


class CartItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemRead(BaseModel):
    product_id: UUID
    product_name: str
    product_sku: str
    unit_price_cents: int
    quantity: int
    line_total_cents: int

    @classmethod
    def from_item(cls, item: CartItem) -> Self:
        """Build a line from a CartItem whose `product` has been eagerly loaded.

        Args:
            item: Cart line with its product relationship populated.

        Returns:
            The line priced at the product's current catalogue price.
        """
        return cls(
            product_id=item.product_id,
            product_name=item.product.name,
            product_sku=item.product.sku,
            unit_price_cents=item.product.price_cents,
            quantity=item.quantity,
            line_total_cents=item.product.price_cents * item.quantity,
        )


class CartRead(BaseModel):
    id: UUID
    user_id: UUID | None
    items: list[CartItemRead]
    total_cents: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_cart(cls, cart: Cart) -> Self:
        """Build the cart view, pricing every line at the live catalogue price.

        Args:
            cart: Cart with `items` and each item's `product` eagerly loaded.

        Returns:
            The cart and its total, recomputed on every read.
        """
        items = [CartItemRead.from_item(item) for item in cart.items]
        return cls(
            id=cart.id,
            user_id=cart.user_id,
            items=items,
            total_cents=sum(item.line_total_cents for item in items),
            created_at=cart.created_at,
            updated_at=cart.updated_at,
        )

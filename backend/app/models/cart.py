from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.product import Product


class Cart(Base, TimestampMixin):
    __tablename__ = "carts"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # Nullable, so an anonymous visitor can hold a cart; unique, so a signed-in
    # user holds at most one. PostgreSQL allows repeated NULLs in a unique index.
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        unique=True,
        index=True,
        default=None,
    )

    items: Mapped[list["CartItem"]] = relationship(
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="raise",
    )


class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_id_product_id"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    cart_id: Mapped[UUID] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
    )
    # No price here on purpose: a cart follows the live catalogue price. Only an
    # order freezes what it charged.
    quantity: Mapped[int] = mapped_column(Integer)

    cart: Mapped[Cart] = relationship(back_populates="items", lazy="raise")
    # lazy="raise" turns an implicit async lazy load — which would fail as
    # MissingGreenlet at runtime — into a loud error in the first test instead.
    product: Mapped[Product] = relationship(lazy="raise")

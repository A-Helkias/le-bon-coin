from enum import StrEnum
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OrderStatus(StrEnum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    CANCELLED = "cancelled"


_STATUS_VALUES = ", ".join(f"'{status}'" for status in OrderStatus)


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(f"status IN ({_STATUS_VALUES})", name="status"),
        CheckConstraint("total_cents >= 0", name="total_cents_positive"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    # Nullable: a guest can order without an account.
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
        default=None,
    )
    status: Mapped[OrderStatus] = mapped_column(
        String(20),
        default=OrderStatus.PENDING,
        server_default=OrderStatus.PENDING,
    )
    # Frozen at checkout, like the line prices: an order is a historical record.
    total_cents: Mapped[int] = mapped_column(Integer)
    customer_email: Mapped[str] = mapped_column(String(255))
    customer_name: Mapped[str] = mapped_column(String(200))
    shipping_address: Mapped[str] = mapped_column(String(255))
    shipping_postal_code: Mapped[str] = mapped_column(String(16))
    shipping_city: Mapped[str] = mapped_column(String(120))
    # ISO 3166-1 alpha-2.
    shipping_country: Mapped[str] = mapped_column(String(2))

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="raise",
    )


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "product_id", name="uq_order_items_order_id_product_id"),
        CheckConstraint("quantity > 0", name="quantity_positive"),
        CheckConstraint("unit_price_cents >= 0", name="unit_price_cents_positive"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    order_id: Mapped[UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
    )
    # Copied at checkout so the order survives a rename, a re-pricing, or a
    # product leaving the catalogue.
    product_name: Mapped[str] = mapped_column(String(200))
    product_sku: Mapped[str] = mapped_column(String(32))
    unit_price_cents: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)

    order: Mapped[Order] = relationship(back_populates="items", lazy="raise")

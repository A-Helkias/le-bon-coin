from uuid import UUID, uuid4

from sqlalchemy import Boolean, CheckConstraint, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price_cents >= 0", name="price_cents_positive"),
        CheckConstraint("stock >= 0", name="stock_positive"),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    sku: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    # Plain indexed text rather than a table: there is no hierarchy, no
    # translation and no display order to manage yet.
    category: Mapped[str | None] = mapped_column(String(50), index=True, default=None)
    # Absolute URL of the product photograph, served by whatever host holds the
    # media. Nullable: a product can be listed before it has been shot.
    image_url: Mapped[str | None] = mapped_column(String(500), default=None)
    # Prices are stored in cents to avoid float rounding.
    price_cents: Mapped[int] = mapped_column(Integer)
    stock: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    # Products are never deleted: orders reference them forever.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

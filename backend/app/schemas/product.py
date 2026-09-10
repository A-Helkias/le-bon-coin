from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=32)
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    price_cents: int = Field(ge=0)
    stock: int = Field(default=0, ge=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    sku: str | None = Field(default=None, min_length=1, max_length=32)
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    price_cents: int | None = Field(default=None, ge=0)
    stock: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    sku: str
    name: str
    description: str | None
    image_url: str | None
    price_cents: int
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

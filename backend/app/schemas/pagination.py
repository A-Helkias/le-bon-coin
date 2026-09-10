from pydantic import BaseModel


class Page[T](BaseModel):
    """Envelope every list route returns."""

    items: list[T]
    total: int

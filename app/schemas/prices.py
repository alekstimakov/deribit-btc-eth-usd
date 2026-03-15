"""Pydantic-схемы ответов API для данных о ценах."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceOut(BaseModel):
    """Одна запись цены."""
    ticker: str
    price: Decimal
    ts_unix: int

    model_config = ConfigDict(from_attributes=True)


class PriceListOut(BaseModel):
    """Список записей цены."""
    items: list[PriceOut]

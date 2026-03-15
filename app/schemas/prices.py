from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceOut(BaseModel):
    ticker: str
    price: Decimal
    ts_unix: int

    model_config = ConfigDict(from_attributes=True)


class PriceListOut(BaseModel):
    items: list[PriceOut]

"""HTTP API для чтения сохраненных цен: all, latest и by_date."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.prices import PriceListOut, PriceOut
from app.services.price_service import get_latest_price, get_prices, get_prices_for_period

# Допустимые тикеры по ТЗ. В Swagger будет выбор только из этих значений.
Ticker = Literal["btc_usd", "eth_usd"]

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/all", response_model=PriceListOut)
def read_all_prices(
    ticker: Ticker = Query(..., description="Выбор валюты"),
    db: Session = Depends(get_db),
) -> PriceListOut:
    """GET /prices/all: все записи по выбранному тикеру."""
    # Возвращает все записи по выбранному тикеру.
    try:
        items = get_prices(db=db, ticker=ticker)
        return PriceListOut(items=items)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/latest", response_model=PriceOut)
def read_latest_price(
    ticker: Ticker = Query(..., description="Выбор валюты"),
    db: Session = Depends(get_db),
) -> PriceOut:
    """GET /prices/latest: последняя запись по тикеру."""
    # Возвращает последнюю цену по тикеру.
    try:
        item = get_latest_price(db=db, ticker=ticker)
        if item is None:
            raise HTTPException(status_code=404, detail="Price not found")
        return item
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/by_date", response_model=PriceListOut)
def read_prices_by_date(
    ticker: Ticker = Query(..., description="Выбор валюты"),
    from_ts: int = Query(..., description="Начало диапазона UNIX timestamp"),
    to_ts: int = Query(..., description="Конец диапазона UNIX timestamp"),
    db: Session = Depends(get_db),
) -> PriceListOut:
    """GET /prices/by_date: записи тикера в заданном диапазоне времени."""
    # Возвращает цены тикера в заданном интервале времени.
    try:
        items = get_prices_for_period(
            db=db,
            ticker=ticker,
            from_ts=from_ts,
            to_ts=to_ts,
        )
        return PriceListOut(items=items)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

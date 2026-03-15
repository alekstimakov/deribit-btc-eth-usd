from collections.abc import Mapping, Sequence
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.models import Price
from app.db.repository import (
    get_all_by_ticker,
    get_latest_by_ticker,
    get_prices_by_date_range,
    insert_prices_batch,
)

ALLOWED_TICKERS = {"btc_usd", "eth_usd"}


def _validate_ticker(ticker: str) -> str:
    normalized = str(ticker).lower()
    if normalized not in ALLOWED_TICKERS:
        raise ValueError(f"Unsupported ticker: {ticker}")
    return normalized


def _validate_ts_range(from_ts: int, to_ts: int) -> tuple[int, int]:
    from_ts_int = int(from_ts)
    to_ts_int = int(to_ts)
    if from_ts_int <= 0 or to_ts_int <= 0:
        raise ValueError("Timestamp values must be > 0")
    if from_ts_int > to_ts_int:
        raise ValueError("from_ts must be <= to_ts")
    return from_ts_int, to_ts_int


def save_prices(db: Session, items: Sequence[Mapping[str, object]]) -> int:
    normalized_items: list[dict[str, object]] = []

    for item in items:
        ticker = _validate_ticker(str(item["ticker"]))
        price = Decimal(str(item["price"]))
        ts_unix = int(item["ts_unix"])

        if price <= 0:
            raise ValueError("Price must be > 0")
        if ts_unix <= 0:
            raise ValueError("Invalid UNIX timestamp")

        normalized_items.append(
            {
                "ticker": ticker,
                "price": price,
                "ts_unix": ts_unix,
            }
        )

    return insert_prices_batch(db=db, items=normalized_items)


def get_prices(db: Session, ticker: str) -> list[Price]:
    return get_all_by_ticker(db=db, ticker=_validate_ticker(ticker))


def get_latest_price(db: Session, ticker: str) -> Price | None:
    return get_latest_by_ticker(db=db, ticker=_validate_ticker(ticker))


def get_prices_for_period(db: Session, ticker: str, from_ts: int, to_ts: int) -> list[Price]:
    normalized_ticker = _validate_ticker(ticker)
    from_ts_int, to_ts_int = _validate_ts_range(from_ts=from_ts, to_ts=to_ts)
    return get_prices_by_date_range(
        db=db,
        ticker=normalized_ticker,
        from_ts=from_ts_int,
        to_ts=to_ts_int,
    )

from collections.abc import Mapping, Sequence
from decimal import Decimal

from sqlalchemy.orm import Session

from app.db.repository import insert_prices_batch

ALLOWED_TICKERS = {"btc_usd", "eth_usd"}


def save_prices(db: Session, items: Sequence[Mapping[str, object]]) -> int:
    # Сервисный слой: проверяем бизнес-правила до обращения к БД.
    for item in items:
        # Приводим вход к ожидаемым типам.
        ticker = str(item["ticker"])
        price = Decimal(str(item["price"]))
        ts_unix = int(item["ts_unix"])

        # Разрешены только тикеры из ТЗ.
        if ticker not in ALLOWED_TICKERS:
            raise ValueError(f"Unsupported ticker: {ticker}")
        # Цена и время должны быть положительными.
        if price <= 0:
            raise ValueError("Price must be > 0")
        if ts_unix <= 0:
            raise ValueError("Invalid UNIX timestamp")

    # После валидации делегируем запись в репозиторий.
    return insert_prices_batch(db=db, items=items)

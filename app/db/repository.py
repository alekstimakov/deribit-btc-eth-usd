from collections.abc import Mapping, Sequence
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Price


def insert_prices_batch(db: Session, items: Sequence[Mapping[str, object]]) -> int:
    saved_count = 0
    try:
        for item in items:
            row = Price(
                ticker=str(item["ticker"]),
                price=Decimal(str(item["price"])),
                ts_unix=int(item["ts_unix"]),
            )
            db.add(row)
            saved_count += 1

        db.commit()
        return saved_count
    except SQLAlchemyError:
        db.rollback()
        raise


def get_all_by_ticker(db: Session, ticker: str) -> list[Price]:
    return (
        db.query(Price)
        .filter(Price.ticker == ticker)
        .order_by(Price.ts_unix.asc())
        .all()
    )


def get_latest_by_ticker(db: Session, ticker: str) -> Price | None:
    return (
        db.query(Price)
        .filter(Price.ticker == ticker)
        .order_by(Price.ts_unix.desc())
        .first()
    )


def get_prices_by_date_range(db: Session, ticker: str, from_ts: int, to_ts: int) -> list[Price]:
    return (
        db.query(Price)
        .filter(
            Price.ticker == ticker,
            Price.ts_unix >= from_ts,
            Price.ts_unix <= to_ts,
        )
        .order_by(Price.ts_unix.asc())
        .all()
    )

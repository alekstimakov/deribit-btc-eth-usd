from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)

from app.db.base import Base


class Price(Base):
    __tablename__ = "prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(16), nullable=False)
    price = Column(Numeric(18, 8), nullable=False)
    ts_unix = Column(BigInteger, nullable=False)

    __table_args__ = (
        # Разрешаем только тикеры из ТЗ.
        CheckConstraint("ticker in ('btc_usd', 'eth_usd')", name="ck_prices_ticker_allowed"),
        # Цена должна быть строго положительной.
        CheckConstraint("price > 0", name="ck_prices_price_positive"),
        # UNIX timestamp должен быть валидным положительным числом.
        CheckConstraint("ts_unix > 0", name="ck_prices_ts_positive"),
        # Защита от дублей одной и той же минуты для одного тикера.
        UniqueConstraint("ticker", "ts_unix", name="uq_prices_ticker_ts"),
        # Ускоряет запросы all/latest/by-date.
        Index("ix_prices_ticker_ts", "ticker", "ts_unix"),
    )


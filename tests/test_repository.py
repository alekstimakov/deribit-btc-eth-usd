from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.repository import (
    get_all_by_ticker,
    get_latest_by_ticker,
    get_prices_by_date_range,
    insert_prices_batch,
)


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Изолированная SQLite-сессия для одного теста repository-слоя."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_insert_and_get_latest(db_session: Session) -> None:
    saved = insert_prices_batch(
        db=db_session,
        items=[
            {"ticker": "btc_usd", "price": "100.1", "ts_unix": 1000},
            {"ticker": "btc_usd", "price": "101.2", "ts_unix": 1060},
        ],
    )
    assert saved == 2

    latest = get_latest_by_ticker(db=db_session, ticker="btc_usd")
    assert latest is not None
    assert latest.ts_unix == 1060


def test_get_prices_by_date_range_and_all(db_session: Session) -> None:
    insert_prices_batch(
        db=db_session,
        items=[
            {"ticker": "eth_usd", "price": "200.0", "ts_unix": 1000},
            {"ticker": "eth_usd", "price": "210.0", "ts_unix": 1060},
            {"ticker": "eth_usd", "price": "220.0", "ts_unix": 1120},
        ],
    )

    all_rows = get_all_by_ticker(db=db_session, ticker="eth_usd")
    assert len(all_rows) == 3

    filtered = get_prices_by_date_range(db=db_session, ticker="eth_usd", from_ts=1000, to_ts=1060)
    assert len(filtered) == 2
    assert [row.ts_unix for row in filtered] == [1000, 1060]

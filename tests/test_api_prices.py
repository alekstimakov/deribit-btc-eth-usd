import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.db.base import Base
from app.db.repository import insert_prices_batch
from app.main import app

# Минимальный набор env-переменных, чтобы Settings() не падал при импорте app.
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("CELERY_BROKER_URL", "redis://localhost:6379/0")
os.environ.setdefault("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
os.environ.setdefault("DERIBIT_BASE_URL", "https://test.deribit.com/api/v2")


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Создает изолированную SQLite-БД в памяти для одного теста."""
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


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Подменяет get_db, чтобы API работал с тестовой SQLite-сессией."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    try:
        yield test_client
    finally:
        app.dependency_overrides.clear()


def _seed_prices(db: Session, items: list[dict]) -> None:
    """Утилита для заполнения тестовых данных в БД."""
    insert_prices_batch(db=db, items=items)


def test_latest_endpoint_returns_row(client: TestClient, db_session: Session) -> None:
    _seed_prices(
        db_session,
        [
            {"ticker": "btc_usd", "price": "10.0", "ts_unix": 1000},
            {"ticker": "btc_usd", "price": "11.0", "ts_unix": 1060},
        ],
    )

    response = client.get("/prices/latest", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    body = response.json()
    assert body["ticker"] == "btc_usd"
    assert body["ts_unix"] == 1060


def test_ticker_validation_422(client: TestClient) -> None:
    response = client.get("/prices/latest", params={"ticker": "doge_usd"})
    assert response.status_code == 422


def test_by_date_endpoint_filters_rows(client: TestClient, db_session: Session) -> None:
    _seed_prices(
        db_session,
        [
            {"ticker": "eth_usd", "price": "20.0", "ts_unix": 1000},
            {"ticker": "eth_usd", "price": "21.0", "ts_unix": 1060},
            {"ticker": "eth_usd", "price": "22.0", "ts_unix": 1120},
        ],
    )

    response = client.get(
        "/prices/by_date",
        params={"ticker": "eth_usd", "from_ts": 1000, "to_ts": 1060},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 2
    assert [row["ts_unix"] for row in body["items"]] == [1000, 1060]

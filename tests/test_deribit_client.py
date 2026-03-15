import asyncio

import pytest

from app.clients.deribit import DeribitClient


class _FakeResponse:
    """Мок ответа aiohttp для контекстного менеджера `async with`."""

    def __init__(self, status: int, payload: dict) -> None:
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        return self._payload


class _FakeSession:
    """Мок aiohttp.ClientSession с методом get()."""

    def __init__(self, response: _FakeResponse) -> None:
        self._response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, url, params=None):
        return self._response


def _patch_client_session(monkeypatch, *, status: int, payload: dict) -> None:
    """Подменяет aiohttp.ClientSession на мок-сессию с заданным ответом."""

    def _fake_client_session(*args, **kwargs):
        return _FakeSession(_FakeResponse(status=status, payload=payload))

    monkeypatch.setattr("app.clients.deribit.aiohttp.ClientSession", _fake_client_session)


def test_get_index_price_success(monkeypatch):
    _patch_client_session(
        monkeypatch,
        status=200,
        payload={
            "result": {"index_price": 123.45},
            "usOut": 1700000000000000,
        },
    )

    client = DeribitClient(base_url="https://test.deribit.com/api/v2")
    result = asyncio.run(client.get_index_price("BTC_USD"))

    assert result["ticker"] == "btc_usd"
    assert result["price"] == 123.45
    assert result["ts_unix"] == 1700000000


def test_get_index_price_http_error(monkeypatch):
    _patch_client_session(
        monkeypatch,
        status=500,
        payload={"error": "bad request"},
    )

    client = DeribitClient(base_url="https://test.deribit.com/api/v2")

    with pytest.raises(ValueError, match="Deribit HTTP error"):
        asyncio.run(client.get_index_price("btc_usd"))

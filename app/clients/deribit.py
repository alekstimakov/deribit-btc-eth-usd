"""Клиент для получения index price с Deribit API."""

import time

import httpx


class DeribitClient:
    """HTTP-клиент Deribit для получения цен по тикерам."""

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        # Базовый URL API (без завершающего "/").
        self.base_url = base_url.rstrip("/")
        # Максимальное время ожидания HTTP-запроса.
        self.timeout = timeout

    async def get_index_price(self, ticker: str) -> dict:
        """Запрашивает index price одного тикера и возвращает payload для сохранения в БД."""
        # Нормализуем тикер к нижнему регистру (btc_usd / eth_usd).
        ticker = ticker.lower()
        # Полный endpoint Deribit для получения index price.
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": ticker}

        # Делаем HTTP-запрос к бирже.
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params)

        # Проверяем статус ответа.
        if response.status_code != 200:
            raise ValueError(f"Deribit HTTP error: {response.status_code}")

        data = response.json()
        result = data.get("result")
        if not result or "index_price" not in result:
            raise ValueError("Deribit response has no index_price")

        # Deribit возвращает usOut в микросекундах. Переводим в UNIX seconds.
        us_out = data.get("usOut")
        ts_unix = int(us_out // 1_000_000) if us_out else int(time.time())

        return {
            "ticker": ticker,
            "price": result["index_price"],
            "ts_unix": ts_unix,
        }

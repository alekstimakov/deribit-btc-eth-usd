"""Клиент для получения index price с Deribit API."""

import time

import aiohttp


class DeribitClient:
    """HTTP-клиент Deribit для получения цен по тикерам."""

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_index_price(self, ticker: str) -> dict:
        """Запрашивает index price одного тикера и возвращает payload для сохранения в БД."""
        ticker = ticker.lower()
        url = f"{self.base_url}/public/get_index_price"
        params = {"index_name": ticker}

        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise ValueError(f"Deribit HTTP error: {response.status}")
                data = await response.json()

        result = data.get("result")
        if not result or "index_price" not in result:
            raise ValueError("Deribit response has no index_price")

        us_out = data.get("usOut")
        ts_unix = int(us_out // 1_000_000) if us_out else int(time.time())

        return {
            "ticker": ticker,
            "price": result["index_price"],
            "ts_unix": ts_unix,
        }

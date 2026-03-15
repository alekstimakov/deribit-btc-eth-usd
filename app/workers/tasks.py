import asyncio

from app.clients.deribit import DeribitClient
from app.config import settings
from app.db.session import SessionLocal
from app.services.price_service import save_prices
from app.workers.celery_app import celery_app


@celery_app.task(name="fetch_and_save_prices")
def fetch_and_save_prices() -> int:
    # Создаем клиент Deribit с URL из конфигурации.
    client = DeribitClient(base_url=settings.deribit_base_url)

    async def _fetch() -> list[dict]:
        # Получаем цены двух обязательных тикеров из ТЗ.
        btc = await client.get_index_price("btc_usd")
        eth = await client.get_index_price("eth_usd")
        # Возвращаем в формате, который ожидает service layer.
        return [btc, eth]

    # Celery-задача синхронная, поэтому запускаем async-функцию через asyncio.run.
    items = asyncio.run(_fetch())

    # Открываем отдельную сессию БД на время выполнения задачи.
    db = SessionLocal()
    try:
        # save_prices:
        # 1) валидирует данные на уровне бизнес-правил,
        # 2) делегирует запись в repository слой.
        return save_prices(db=db, items=items)
    finally:
        # Обязательно закрываем сессию даже при ошибках,
        # чтобы не оставлять “висящие” соединения.
        db.close()

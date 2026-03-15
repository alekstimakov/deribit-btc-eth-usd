# Crypto2

Сервис каждую минуту получает `btc_usd` и `eth_usd` (index price) с Deribit, сохраняет их в PostgreSQL и отдает данные через FastAPI.

## Что внутри

- FastAPI API (`/prices/all`, `/prices/latest`, `/prices/by_date`)
- PostgreSQL
- Celery worker + beat (периодический сбор раз в минуту)
- Deribit client на `aiohttp`
- Alembic миграции
- Unit-тесты (`pytest`)

## Быстрый запуск (Docker)

1. Клонировать репозиторий и перейти в папку проекта.
2. Запустить:

```bash
docker compose up -d --build
```

3. Проверить:

```bash
docker compose ps
```

4. Открыть Swagger:

`http://127.0.0.1:8000/docs`

## API

Во всех методах обязательный query-параметр `ticker`.

Допустимые значения:
- `btc_usd`
- `eth_usd`

Методы:
- `GET /prices/all?ticker=btc_usd`
- `GET /prices/latest?ticker=eth_usd`
- `GET /prices/by_date?ticker=btc_usd&from_ts=1700000000&to_ts=1700003600`

## Проверка, что данные пишутся

Логи Celery:

```bash
docker compose logs -f worker
docker compose logs -f beat
```

Проверка БД:

```bash
docker exec -it crypto2-postgres psql -U postgres -d crypto2
```

```sql
SELECT id, ticker, price, ts_unix
FROM prices
ORDER BY id DESC
LIMIT 20;
```

## Локальный запуск (без Docker)

1. Установить зависимости:

```bash
pip install -r requirements.txt
```

2. Поднять `postgres` и `redis` (например, через Docker).
3. Применить миграции:

```bash
alembic upgrade head
```

4. Запустить API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

5. На Windows запустить Celery:
- `start_celery_windows.bat`
- остановка: `stop_celery_windows.bat`

## Тесты

```bash
pytest -q
```

## Design decisions

1. Разделение на слои `client -> service -> repository -> api` для читаемости и тестируемости.
2. `Decimal` для цен вместо `float`.
3. `ticker` обязателен в каждом API-методе по требованиям ТЗ.
4. Celery Beat + Worker для периодического сбора цен.
5. `aiohttp` в клиенте Deribit (необязательное требование ТЗ).

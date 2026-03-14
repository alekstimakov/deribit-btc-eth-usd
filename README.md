# Crypto2

Сервис собирает index price для `btc_usd` и `eth_usd` с Deribit каждую минуту и сохраняет значения в PostgreSQL.

## What Is Included

- FastAPI API для чтения сохраненных данных
- Celery worker и beat для периодического сбора цен
- PostgreSQL как основная БД
- Alembic для миграций

## Runbook (Draft)

Подробные команды запуска и разворачивания будут добавлены после реализации.

## Design Decisions (Draft)

- Единая таблица `prices` для всех тикеров
- `ticker` обязателен в каждом API-методе
- Периодический сбор через Celery Beat раз в минуту


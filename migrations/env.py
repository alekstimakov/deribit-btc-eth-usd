from logging.config import fileConfig
import os
from pathlib import Path
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Добавляем корень проекта в начало sys.path, чтобы импортировался локальный пакет app,
# а не одноименный пакет из site-packages.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.base import Base
import app.db.models  # noqa: F401


config = context.config

# Use DATABASE_URL from environment when available (important for Docker).
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)

if config.config_file_name is not None:
    # Подключаем конфиг логирования из alembic.ini:
    # так в консоли будут понятные сообщения Alembic/SQLAlchemy.
    fileConfig(config.config_file_name)

# Здесь хранится "карта" всех таблиц SQLAlchemy.
# Alembic сравнивает эту metadata с текущей БД при --autogenerate
# и на основе разницы генерирует миграции.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    # OFFLINE-режим:
    # Alembic не открывает реальное соединение с БД,
    # а генерирует SQL-операции "на бумаге" (например, для вывода SQL-скрипта).
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        # Вставлять значения прямо в SQL (без bind-параметров).
        literal_binds=True,
        # Формат параметров для SQL-диалекта.
        dialect_opts={"paramstyle": "named"},
    )

    # Транзакция миграции в offline-сценарии.
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # ONLINE-режим:
    # обычный сценарий, когда Alembic подключается к PostgreSQL
    # и применяет миграции напрямую к базе.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        # Для миграций пул соединений обычно не нужен.
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Передаем Alembic активное соединение + metadata моделей.
        context.configure(connection=connection, target_metadata=target_metadata)

        # Транзакция миграции в online-сценарии.
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    # Если запущен offline-режим, идем по offline-пути.
    run_migrations_offline()
else:
    # Иначе (по умолчанию) применяем миграции к реальной БД.
    run_migrations_online()


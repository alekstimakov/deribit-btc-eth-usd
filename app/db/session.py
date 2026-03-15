"""Инициализация SQLAlchemy engine и фабрики сессий."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings


# Engine — “движок” SQLAlchemy, который держит соединение/пул и знает,
# как подключаться к конкретной БД.
engine = create_engine(settings.database_url, future=True)

# SessionLocal — фабрика сессий.
# Каждый вызов SessionLocal() создает отдельную Session для запроса/задачи.
# autocommit=False: коммит делаем явно (через db.commit()).
# autoflush=False: SQLAlchemy не отправляет изменения в БД автоматически
# перед каждым SELECT, что делает поведение более предсказуемым.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

"""Инициализация Celery-приложения и регистрация задач/расписания."""

from celery import Celery

from app.config import settings


# Инициализируем Celery-приложение:
# - имя приложения используется как идентификатор
# - broker хранит очередь задач
# - backend хранит результат выполненных задач
celery_app = Celery(
    "price_every_minute",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Работаем в UTC, чтобы расписание и timestamp были единообразными
# независимо от локальной таймзоны сервера/разработчика.
celery_app.conf.timezone = "UTC"
celery_app.conf.enable_utc = True

# Импортируем модули после создания celery_app.
# Это важно: при импорте tasks/beat происходит регистрация задач и расписания.
# noqa подавляет предупреждения линтера:
# F401 — импорт “не используется” (он нужен ради сайд-эффекта регистрации),
# E402 — импорт не в начале файла (здесь это осознанно).
import app.workers.tasks  # noqa: F401,E402
import app.workers.beat_schedule  # noqa: F401,E402

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Параметры запуска FastAPI (host/port для uvicorn).
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # Полный URL подключения к PostgreSQL.
    # Пример: postgresql+psycopg2://postgres:postgres@localhost:5432/crypto2
    database_url: str

    # Redis broker для очереди задач Celery.
    celery_broker_url: str
    # Хранилище результатов задач Celery (обычно тоже Redis).
    celery_result_backend: str

    # Базовый URL API Deribit (testnet/mainnet выбирается через .env).
    deribit_base_url: str

    # Настройка загрузки переменных окружения:
    # - читаем из .env
    # - ожидаем UTF-8
    # - не требуем строгого регистра имен переменных
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# При импорте модуля сразу создаем объект настроек.
# Если обязательной переменной нет (например DATABASE_URL) — приложение упадет
# на старте, что лучше, чем скрытая ошибка во время работы.
settings = Settings()

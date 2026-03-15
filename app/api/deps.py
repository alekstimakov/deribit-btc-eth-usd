from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    # Создаем отдельную сессию БД на время одного HTTP-запроса.
    db = SessionLocal()
    try:
        # Передаем сессию в endpoint через Depends(get_db).
        yield db
    finally:
        # Гарантированно закрываем сессию после завершения запроса.
        db.close()

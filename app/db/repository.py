from collections.abc import Mapping, Sequence
from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Price


def insert_prices_batch(db: Session, items: Sequence[Mapping[str, object]]) -> int:
    saved_count = 0
    try:
        for item in items:
            # ORM-объект = будущая строка таблицы prices.
            row = Price(
                ticker=str(item["ticker"]),
                price=Decimal(str(item["price"])),
                ts_unix=int(item["ts_unix"]),
            )
            # Добавляем в текущую транзакцию.
            db.add(row)
            saved_count += 1

        # Фиксируем все изменения в БД одной операцией.
        db.commit()
        return saved_count
    except SQLAlchemyError:
        # Если запись не удалась, откатываем всю пачку.
        db.rollback()
        raise

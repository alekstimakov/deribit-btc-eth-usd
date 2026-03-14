
def save_price(db, items) -> int:
    saved_count = 0
    allowed_ticker = {'btc_usd', 'eth_usd'}

    try:
        for item in items:
            ticker = item['ticker']
            price = item['price']
            ts_unix = item['ts_unix']

            if ticker not in allowed_ticker:
                raise ValueError(f'Неподдерживаемый тикер {ticker}')
            if price <= 0:
                raise ValueError(f'Цена меньше нуля')
            if ts_unix <= 0:
                raise ValueError(f'Некорректный timestamp')

            row = Price(ticker=ticker, price=price, ts_unix=ts_unix)
            db.add(row)
            saved_count += 1
        db.commit()
        return saved_count
    except Exception:
        db.rollback()
        raise

from app.db.models import Price


def save_price(db, items) -> int:
    # Счетчик успешно добавленных записей.
    saved_count = 0
    # Разрешаем только тикеры из ТЗ.
    allowed_ticker = {"btc_usd", "eth_usd"}

    try:
        # Обрабатываем входные элементы по одному.
        for item in items:
            ticker = item["ticker"]
            price = item["price"]
            ts_unix = item["ts_unix"]

            # Базовая валидация входных данных.
            if ticker not in allowed_ticker:
                raise ValueError(f"Неподдерживаемый тикер: {ticker}")
            if price <= 0:
                raise ValueError("Цена должна быть > 0")
            if ts_unix <= 0:
                raise ValueError("Некорректный timestamp")

            # Создаем ORM-объект и добавляем в текущую транзакцию.
            row = Price(ticker=ticker, price=price, ts_unix=ts_unix)
            db.add(row)
            saved_count += 1

        # Фиксируем все добавленные записи в БД.
        db.commit()
        return saved_count
    except Exception:
        # Если что-то пошло не так, откатываем транзакцию.
        db.rollback()
        raise

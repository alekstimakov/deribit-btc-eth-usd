from celery.schedules import crontab

from app.workers.celery_app import celery_app


# Расписание Celery Beat:
# ключ "fetch-prices-every-minute" — произвольное имя расписания.
# task — имя зарегистрированной Celery-задачи из декоратора @celery_app.task(...).
# schedule — cron-правило: запуск каждую минуту.
celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "fetch_and_save_prices",
        "schedule": crontab(minute="*"),
    }
}

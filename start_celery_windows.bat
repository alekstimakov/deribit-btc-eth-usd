@echo off
setlocal

REM Run from the project root.
cd /d "%~dp0"

REM Default env vars (can be overridden if already set).
if not defined DATABASE_URL set "DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/crypto2"
if not defined CELERY_BROKER_URL set "CELERY_BROKER_URL=redis://localhost:6379/0"
if not defined CELERY_RESULT_BACKEND set "CELERY_RESULT_BACKEND=redis://localhost:6379/1"
if not defined DERIBIT_BASE_URL set "DERIBIT_BASE_URL=https://test.deribit.com/api/v2"

echo Starting Celery worker and beat in separate windows...
echo.
echo DATABASE_URL=%DATABASE_URL%
echo CELERY_BROKER_URL=%CELERY_BROKER_URL%
echo CELERY_RESULT_BACKEND=%CELERY_RESULT_BACKEND%
echo DERIBIT_BASE_URL=%DERIBIT_BASE_URL%
echo.

start "crypto2-celery-worker" cmd /k "cd /d %~dp0 && celery -A app.workers.celery_app:celery_app worker --loglevel=info --pool=solo"
start "crypto2-celery-beat" cmd /k "cd /d %~dp0 && celery -A app.workers.celery_app:celery_app beat --loglevel=debug"

echo Started:
echo - crypto2-celery-worker
echo - crypto2-celery-beat
echo.
echo To stop both: run stop_celery_windows.bat

endlocal

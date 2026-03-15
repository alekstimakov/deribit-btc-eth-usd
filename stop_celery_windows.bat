@echo off
setlocal

echo Stopping Celery windows...

taskkill /FI "WINDOWTITLE eq crypto2-celery-worker" /T /F >nul 2>&1
if %errorlevel%==0 (
  echo Stopped: crypto2-celery-worker
) else (
  echo Not running: crypto2-celery-worker
)

taskkill /FI "WINDOWTITLE eq crypto2-celery-beat" /T /F >nul 2>&1
if %errorlevel%==0 (
  echo Stopped: crypto2-celery-beat
) else (
  echo Not running: crypto2-celery-beat
)

endlocal

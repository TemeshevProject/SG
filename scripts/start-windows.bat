@echo off
chcp 65001 >nul
echo Калькулятор АПК Сергек — локальный запуск
echo.

where python >nul 2>&1 || (echo Установите Python 3: https://python.org & pause & exit /b 1)
where npm >nul 2>&1 || (echo Установите Node.js: https://nodejs.org & pause & exit /b 1)

cd /d "%~dp0.."

echo Установка зависимостей...
pip install -q -r backend\requirements.txt
if not exist frontend\node_modules (cd frontend && call npm install && cd ..)

start "APK Backend" cmd /k "cd /d %~dp0..\backend && set PYTHONPATH=. && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 2 /nobreak >nul
start "APK Frontend" cmd /k "cd /d %~dp0..\frontend && npm run dev"

echo.
echo Откройте в браузере: http://localhost:5173
echo Закройте окна Backend и Frontend для остановки.
pause

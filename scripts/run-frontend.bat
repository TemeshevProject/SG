@echo off
chcp 65001 >nul
title APK Frontend (порт 5173)

set "ROOT=%~dp0.."
cd /d "%ROOT%\frontend"

echo Frontend: %CD%
echo.
echo Не закрывайте это окно!
echo После запуска откройте: http://localhost:5173
echo.

if not exist "node_modules\" (
  echo Установка npm-пакетов, подождите...
  call npm install
  if errorlevel 1 (
    echo ОШИБКА npm install
    pause
    exit /b 1
  )
)

call npm run dev -- --host 127.0.0.1 --port 5173

echo.
echo Frontend остановлен.
pause

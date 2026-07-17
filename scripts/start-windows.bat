@echo off
chcp 65001 >nul
title Запуск калькулятора АПК Сергек

echo ========================================
echo   Калькулятор АПК Сергек
echo ========================================
echo.

set "ROOT=%~dp0.."
cd /d "%ROOT%"

if not exist "backend\app\main.py" (
  echo ОШИБКА: Запускайте из папки SG, где есть backend и frontend.
  echo Сейчас: %CD%
  pause
  exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo ОШИБКА: Не найден Python. Установите с https://python.org
    echo Сначала запустите: scripts\check-system.bat
    pause
    exit /b 1
  )
)

where npm >nul 2>&1
if errorlevel 1 (
  echo ОШИБКА: Не найден Node.js. Установите с https://nodejs.org
  pause
  exit /b 1
)

echo Установка Python-зависимостей...
where python >nul 2>&1 && (
  pip install -r backend\requirements.txt
) || (
  py -3 -m pip install -r backend\requirements.txt
)
if errorlevel 1 (
  echo ОШИБКА при pip install
  pause
  exit /b 1
)

if not exist "frontend\node_modules\" (
  echo Установка npm-пакетов, подождите 1-2 минуты...
  cd frontend
  call npm install
  if errorlevel 1 (
    echo ОШИБКА npm install
    pause
    exit /b 1
  )
  cd ..
)

echo.
echo Запускаю Backend и Frontend в отдельных окнах...
echo.

start "APK Backend" cmd /k ""%~dp0run-backend.bat""
timeout /t 3 /nobreak >nul
start "APK Frontend" cmd /k ""%~dp0run-frontend.bat""

echo.
echo ========================================
echo   Готово!
echo.
echo   1. Должны открыться ДВА новых окна:
echo      - APK Backend
echo      - APK Frontend
echo.
echo   2. Подождите 10-20 секунд
echo.
echo   3. Откройте в браузере:
echo      http://localhost:5173
echo.
echo   Если не работает — запустите check-system.bat
echo   и пришлите скрин всех окон.
echo ========================================
echo.
pause

@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo   Проверка системы — Калькулятор АПК
echo ========================================
echo.

set "OK=1"

echo [1] Папка скрипта:
echo     %~dp0
echo.

echo [2] Python:
where python >nul 2>&1 && (python --version && echo     OK: python) || (
  where py >nul 2>&1 && (py -3 --version && echo     OK: py -3) || (
    echo     ОШИБКА: Python не найден. Установите с python.org
    set "OK=0"
  )
)
echo.

echo [3] pip:
where pip >nul 2>&1 && (pip --version && echo     OK) || (
  py -3 -m pip --version >nul 2>&1 && (py -3 -m pip --version && echo     OK: py -3 -m pip) || (
    echo     ОШИБКА: pip не найден
    set "OK=0"
  )
)
echo.

echo [4] Node.js:
where node >nul 2>&1 && (node --version && echo     OK) || (
  echo     ОШИБКА: Node.js не найден. Установите с nodejs.org
  set "OK=0"
)
echo.

echo [5] npm:
where npm >nul 2>&1 && (npm --version && echo     OK) || (
  echo     ОШИБКА: npm не найден
  set "OK=0"
)
echo.

set "ROOT=%~dp0.."
cd /d "%ROOT%"
echo [6] Папка проекта:
echo     %CD%
if exist "backend\app\main.py" (echo     OK: backend найден) else (
  echo     ОШИБКА: нет backend\app\main.py — неверная папка?
  set "OK=0"
)
if exist "frontend\package.json" (echo     OK: frontend найден) else (
  echo     ОШИБКА: нет frontend\package.json
  set "OK=0"
)
echo.

if "%OK%"=="1" (
  echo ========================================
  echo   Все проверки пройдены. Можно запускать start-windows.bat
  echo ========================================
) else (
  echo ========================================
  echo   Есть ошибки — исправьте и запустите снова
  echo ========================================
)

echo.
pause

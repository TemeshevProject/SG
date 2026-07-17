@echo off
chcp 65001 >nul
title APK Backend (порт 8000)

set "ROOT=%~dp0.."
cd /d "%ROOT%\backend"

set "PYTHONPATH=."
set "PYCMD=python"

where python >nul 2>&1 || set "PYCMD=py -3"

echo Backend: %CD%
echo Команда: %PYCMD% -m uvicorn app.main:app --port 8000
echo.
echo Не закрывайте это окно!
echo.

%PYCMD% -m pip install -r requirements.txt
%PYCMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo Backend остановлен. Код ошибки: %ERRORLEVEL%
pause

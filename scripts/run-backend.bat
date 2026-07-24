@echo off
title APK Backend - port 8000
set "ROOT=%~dp0.."
cd /d "%ROOT%\backend" 2>nul
if errorlevel 1 (
  echo OSHIBKA: ne naydena papka backend
  echo %ROOT%\backend
  pause
  exit /b 1
)

set "PYTHONPATH=."
set "PYCMD=python"
where python >nul 2>&1 || set "PYCMD=py -3"

echo ========================================
echo  BACKEND
echo  Papka: %CD%
echo ========================================
echo.

echo Ustanovka paketov...
%PYCMD% -m pip install -r requirements.txt
if errorlevel 1 echo VNIMANIE: oshibka pip - prodolzhaem...

echo.
echo Zapusk servera na http://127.0.0.1:8000
echo NE ZAKRYVAYTE eto okno!
echo.

%PYCMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo Backend ostanovlen. Kod: %ERRORLEVEL%
pause

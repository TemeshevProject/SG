@echo off
title APK Backend - port 8000
set "ROOT=%~dp0.."
cd /d "%ROOT%\backend" 2>nul
if errorlevel 1 (
  echo OSHIBKA: ne naydena papka backend
  pause
  exit /b 1
)

call "%~dp0pick-python.bat"
if errorlevel 1 exit /b 1

set "PYTHONPATH=."

echo ========================================
echo  BACKEND
echo  Papka: %CD%
echo ========================================
echo.
%PYCMD% --version
echo.

echo Ustanovka paketov (pip)...
%PYCMD% -m pip install --upgrade pip >> "%ROOT%install-log.txt" 2>&1
%PYCMD% -m pip install -r requirements.txt >> "%ROOT%install-log.txt" 2>&1
if errorlevel 1 (
  echo.
  echo OSHIBKA pip install!
  echo Skoree vsego ustanovlen Python 3.14 - nuzhen Python 3.12
  echo Sm. fayl: USTANOVKA-PYTHON.txt
  echo Log: %ROOT%install-log.txt
  pause
  exit /b 1
)

echo.
echo Zapusk servera: http://127.0.0.1:8000
echo NE ZAKRYVAYTE eto okno!
echo.

%PYCMD% -m uvicorn app.main:app --host 127.0.0.1 --port 8000

echo.
echo Backend ostanovlen. Kod: %ERRORLEVEL%
pause

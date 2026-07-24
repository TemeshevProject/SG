@echo off
chcp 65001 >nul
title Kalkulyator APK Sergek
setlocal

set "ROOT=%~dp0"
set "LOG=%ROOT%install-log.txt"
cd /d "%ROOT%"

echo [%DATE% %TIME%] Start >> "%LOG%"

echo.
echo  ============================================
echo    Kalkulyator APK Sergek - ZAPUSK
echo  ============================================
echo.
echo  Papka: %CD%
echo  Log:   %LOG%
echo.

REM --- Python ---
set "PY=python"
where python >nul 2>&1 || set "PY=py -3"
where python >nul 2>&1 || where py >nul 2>&1
if errorlevel 1 (
  echo [OSHIBKA] Python ne ustanovlen!
  echo Ustanovite: https://www.python.org/downloads/
  echo Otmette: Add python.exe to PATH
  echo [OSHIBKA] Python >> "%LOG%"
  goto :end
)
echo [OK] Python
%PY% --version >> "%LOG%" 2>&1

REM --- Node ---
where node >nul 2>&1
if errorlevel 1 (
  echo [OSHIBKA] Node.js ne ustanovlen!
  echo Ustanovite: https://nodejs.org/  ^(LTS^)
  echo [OSHIBKA] Node >> "%LOG%"
  goto :end
)
echo [OK] Node.js
node --version >> "%LOG%" 2>&1

if not exist "backend\app\main.py" (
  echo [OSHIBKA] Ne ta papka! Net backend\app\main.py
  goto :end
)

echo.
echo [1/3] Ustanovka Python paketov...
%PY% -m pip install -r backend\requirements.txt >> "%LOG%" 2>&1
if errorlevel 1 (
  echo [OSHIBKA] pip install - sm. install-log.txt
  goto :end
)
echo       Gotovo.

echo [2/3] Ustanovka npm paketov ^(1-3 min^)...
if not exist "frontend\node_modules\" (
  cd frontend
  call npm install >> "%LOG%" 2>&1
  if errorlevel 1 (
    echo [OSHIBKA] npm install - sm. install-log.txt
    cd ..
    goto :end
  )
  cd ..
)
echo       Gotovo.

echo [3/3] Zapusk serverov...
echo.

start "APK-Backend" cmd /k "cd /d "%ROOT%backend" && set PYTHONPATH=. && %PY% -m uvicorn app.main:app --host 127.0.0.1 --port 8000"
timeout /t 4 /nobreak >nul
start "APK-Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev -- --host 127.0.0.1 --port 5173"

echo.
echo  ============================================
echo    Otkroyte 2 novyh okna: APK-Backend i APK-Frontend
echo    Podozhdite 20 sekund
echo    Brauzer:  http://localhost:5173
echo  ============================================
echo.
echo  Esli ne rabotaet:
echo  1. Perezapustite etot fayl ot imeni administratora
echo  2. Peremestite papku v C:\SG  ^(bez kirillicy v puti^)
echo  3. Prishlite fayl install-log.txt
echo.

:end
pause

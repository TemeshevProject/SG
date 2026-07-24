@echo off
chcp 65001 >nul
title Kalkulyator APK Sergek
setlocal EnableExtensions

set "ROOT=%~dp0"
set "LOG=%ROOT%install-log.txt"
cd /d "%ROOT%"

echo. > "%LOG%"
echo [%DATE% %TIME%] START >> "%LOG%"

echo.
echo  ============================================
echo    Kalkulyator APK Sergek
echo  ============================================
echo  Papka: %CD%
echo.

set "PY=python"
call "%ROOT%scripts\pick-python.bat" 2>nul
if defined PYCMD set "PY=%PYCMD%"

where %PY% >nul 2>&1
if errorlevel 1 (
  echo [OSHIBKA] Net Python 3.12. Sm. USTANOVKA-PYTHON.txt
  goto :finish
)
echo [OK] Python
%PY% --version

where node >nul 2>&1
if errorlevel 1 (
  echo [OSHIBKA] Net Node.js. Ustanovite s nodejs.org ^(LTS^)
  goto :finish
)
echo [OK] Node.js
node --version

if not exist "%ROOT%backend\app\main.py" (
  echo [OSHIBKA] Zapuskayte START.bat iz papki gde est backend i frontend!
  goto :finish
)

echo.
echo Ustanovka paketov (sm. install-log.txt)...
%PY% -m pip install -r "%ROOT%backend\requirements.txt" >> "%LOG%" 2>&1

if not exist "%ROOT%frontend\node_modules\" (
  echo npm install - podozhdite...
  pushd "%ROOT%frontend"
  call npm install >> "%LOG%" 2>&1
  popd
)

echo.
echo Otkryvayu okno BACKEND...
start "APK-Backend" cmd /k call "%ROOT%scripts\run-backend.bat"

timeout /t 2 /nobreak >nul

echo Otkryvayu okno FRONTEND...
start "APK-Frontend" cmd /k call "%ROOT%scripts\run-frontend.bat"

echo.
echo  ============================================
echo  Dolzhny otkrytsya 2 okna:
echo    APK-Backend  i  APK-Frontend
echo.
echo  Podozhdite 30 sek, zatem brauzer:
echo    http://localhost:5173
echo.
echo  Esli okon net - zapustite vruchnuyu:
echo    1-BACKEND.bat  i  2-FRONTEND.bat
echo  ============================================

:finish
echo.
pause

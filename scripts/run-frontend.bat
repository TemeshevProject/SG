@echo off
title APK Frontend - port 5173
set "ROOT=%~dp0.."
cd /d "%ROOT%\frontend" 2>nul
if errorlevel 1 (
  echo OSHIBKA: ne naydena papka frontend
  pause
  exit /b 1
)

echo ========================================
echo  FRONTEND
echo  Papka: %CD%
echo ========================================
echo.

where node >nul 2>&1
if errorlevel 1 (
  echo OSHIBKA: Node.js ne ustanovlen!
  echo Skachayte: https://nodejs.org/
  pause
  exit /b 1
)

if not exist "node_modules\" (
  echo npm install - podozhdite 1-3 min...
  call npm install
  if errorlevel 1 (
    echo OSHIBKA npm install
    pause
    exit /b 1
  )
)

echo Zapusk na http://localhost:5173
echo NE ZAKRYVAYTE eto okno!
echo.

call npm run dev -- --host 127.0.0.1 --port 5173

echo.
echo Frontend ostanovlen.
pause

@echo off
echo.
echo ========================================
echo   Eto okno dolzhno OSTATSJA otkrytym
echo ========================================
echo.
echo Papka skripta: %~dp0
echo.
pause
cd /d "%~dp0.."
echo Papka proekta: %CD%
echo.
echo Proverka Python:
python --version
if errorlevel 1 echo Python NE NAYDEN - poprobuyte: py -3 --version
echo.
echo Proverka Node:
node --version
if errorlevel 1 echo Node NE NAYDEN
echo.
echo Proverka npm:
npm --version
if errorlevel 1 echo npm NE NAYDEN
echo.
echo Esli vyshe oshibki - ustanovite Python i Node.js
echo Sm. fail START-HERE.txt v papke SG
echo.
pause

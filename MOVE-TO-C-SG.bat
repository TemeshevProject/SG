@echo off
chcp 65001 >nul
echo.
echo ========================================
echo   PEREMESCHENIE PROEKTA V C:\SG
echo ========================================
echo.
echo Kirillica v puti (napr. cursor_apk) chasto lomaet npm i Python.
echo Etot skript skopiruet proekt v C:\SG
echo.
pause

if not exist "C:\SG" mkdir "C:\SG"
xcopy /E /I /Y "%~dp0*" "C:\SG\" >nul
echo.
echo Gotovo! Proekt skopirovan v:
echo   C:\SG
echo.
echo Teper:
echo   1. Otkroyte papku C:\SG
echo   2. Zapustite START.bat
echo.
explorer C:\SG
pause

@echo off
chcp 65001 >nul
echo.
echo ============================================================
echo   Ustanovka Python 3.12 (obyazatelno dlya etogo proekta)
echo ============================================================
echo.
echo U vas Python 3.14 - on NE podderzhivaetsya (net gotovyh paketov).
echo.
echo Otkroetsya stranitsa skachivaniya Python 3.12.10:
echo.
echo   1. Skachayte "Windows installer (64-bit)"
echo   2. Pri ustanovke VKLYUCHITE galochku "Add python.exe to PATH"
echo   3. Posle ustanovki zapustite 1-BACKEND.bat snova
echo.
pause
start https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe
exit /b 0

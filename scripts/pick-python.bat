@echo off
REM Vybor Python 3.11 ili 3.12 (NE 3.14!)
set "PYCMD="

py -3.12 -c "import sys" >nul 2>&1 && set "PYCMD=py -3.12" && goto :done
py -3.11 -c "import sys" >nul 2>&1 && set "PYCMD=py -3.11" && goto :done
py -3.10 -c "import sys" >nul 2>&1 && set "PYCMD=py -3.10" && goto :done

where python >nul 2>&1
if not errorlevel 1 (
  for /f "tokens=2" %%v in ('python -c "import sys; print(sys.version_info[1])" 2^>nul') do set "PYMINOR=%%v"
  if defined PYMINOR if %PYMINOR% GEQ 14 (
    echo.
    echo ========================================
    echo  OSHIBKA: U vas Python 3.%PYMINOR%
    echo  Dlya etogo proekta nuzhen Python 3.12
    echo ========================================
    echo.
    echo Skachayte i ustanovite:
    echo  https://www.python.org/downloads/release/python-31210/
    echo.
    echo Pri ustanovke otmette: Add python.exe to PATH
    echo Perezagruzite PK i zapustite snova.
    echo.
    pause
    exit /b 1
  )
  set "PYCMD=python"
  goto :done
)

echo Python ne nayden. Ustanovite Python 3.12 s python.org
pause
exit /b 1

:done
exit /b 0

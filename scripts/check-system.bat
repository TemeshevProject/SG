@echo off
cd /d "%~dp0.."
set LOG=%~dp0check-result.txt
echo === CHECK === > "%LOG%"
echo Papka: %CD% >> "%LOG%"
echo. >> "%LOG%"
echo Python: >> "%LOG%"
where python >> "%LOG%" 2>&1
python --version >> "%LOG%" 2>&1
where py >> "%LOG%" 2>&1
py -3 --version >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo Node: >> "%LOG%"
where node >> "%LOG%" 2>&1
node --version >> "%LOG%" 2>&1
npm --version >> "%LOG%" 2>&1
echo. >> "%LOG%"
if exist backend\app\main.py (echo OK backend >> "%LOG%") else (echo NET backend >> "%LOG%")
if exist frontend\package.json (echo OK frontend >> "%LOG%") else (echo NET frontend >> "%LOG%")
start notepad "%LOG%"

@echo off

REM Move to Django project directory
cd /d C:\Projects\pms-v1

REM Activate virtual environment
call C:\Projects\env\Scripts\activate

REM Check if MySQL (port 3306) is running
netstat -ano | find ":3306" > nul
IF ERRORLEVEL 1 (
    echo MySQL not running. Starting Laragon services...
    start "" "C:\laragon\laragon.exe" start
    timeout /t 10 > nul
) ELSE (
    echo MySQL is already running.
)

REM Start Django development server (keep terminal open)
start cmd /k python manage.py runserver

REM Wait for server to boot
timeout /t 3 > nul

REM Open Chrome in App Mode
start "" chrome --app=http://127.0.0.1:8000/

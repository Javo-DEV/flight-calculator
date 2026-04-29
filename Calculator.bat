@echo off
echo ========================================
echo   MSFS 2020 Flight Calculator
echo ========================================
echo.

cd /d "%~dp0"

REM Check if venv exists
if not exist ".venv\Scripts\python.exe" (
    echo Virtual Environment nicht gefunden!
    echo Erstelle neues Virtual Environment...
    python -m venv .venv
    echo.
    echo Installiere Dependencies...
    .venv\Scripts\python.exe -m pip install -r requirements.txt
)

REM Activate and run
echo Starte Flight Calculator...
echo.
.venv\Scripts\python.exe -m streamlit run app.py

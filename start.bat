@echo off
set VIRTUAL_ENV=%~dp0.venv
set PATH=%~dp0.venv\Scripts;%PATH%
python -m streamlit run app.py
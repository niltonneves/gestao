@echo off
rem Inicializador N7 Gestão – Windows
cd /d "%~dp0"
set FLASK_APP=run.py
set FLASK_DEBUG=1
python run.py

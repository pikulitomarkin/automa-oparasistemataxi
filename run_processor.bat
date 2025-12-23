@echo off
REM Script para rodar o processador no Windows

cd /d %~dp0
call venv\Scripts\activate.bat
python -m src.processor
pause

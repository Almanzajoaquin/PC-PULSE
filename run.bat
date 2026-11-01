@echo off
title PC-Pulse Optimizer
:: Solicitar permisos de Administrador automaticamente
net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
echo Checking Python dependencies...
python -m pip install -r requirements.txt --quiet
cls
python main.py
pause
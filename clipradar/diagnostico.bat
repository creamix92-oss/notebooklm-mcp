@echo off
rem ClipRadar - prueba todas las piezas y abre un informe
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (echo Primero abre run.bat para instalar. & pause & exit /b 1)
echo Probando ClipRadar, tarda unos 5 minutos. No cierres esta ventana...
.venv\Scripts\python -m app.diagnose
start notepad diagnostico.txt
pause

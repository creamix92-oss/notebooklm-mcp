@echo off
rem ClipRadar - arranque en Windows (doble clic)
cd /d "%~dp0"
where python >nul 2>nul || (echo Instala Python 3.10 o superior desde https://www.python.org/downloads/ y marca "Add to PATH". & pause & exit /b 1)
if not exist .venv (
  echo Preparando ClipRadar por primera vez, tarda unos minutos...
  python -m venv .venv || (pause & exit /b 1)
  .venv\Scripts\python -m pip install --upgrade pip -q
  .venv\Scripts\pip install -r requirements.txt || (pause & exit /b 1)
)
.venv\Scripts\python -m app
pause

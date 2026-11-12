@echo off
rem ClipRadar - arranque en Windows (doble clic)
setlocal
cd /d "%~dp0"
set "PY312=%LocalAppData%\Programs\Python\Python312\python.exe"
set "CHECK=import struct,sys; sys.exit(0 if struct.calcsize('P')==8 and (3,10)<=sys.version_info[:2]<=(3,13) else 1)"
set "PYEXE="

rem --- 1. Buscar un Python compatible (3.10 a 3.13, 64 bits) ---
for %%V in (3.12 3.11 3.13 3.10) do call :trypy %%V
if defined PYEXE goto havepy
if exist "%PY312%" set "PYEXE="%PY312%""
if defined PYEXE goto havepy
python -c "%CHECK%" >nul 2>nul && set "PYEXE=python"
if defined PYEXE goto havepy

rem --- 2. No hay: instalar Python 3.12 automaticamente ---
echo No encontre un Python compatible. Instalando Python 3.12 (64 bits)...
winget install -e --id Python.Python.3.12 --scope user --accept-package-agreements --accept-source-agreements
if exist "%PY312%" set "PYEXE="%PY312%""
if defined PYEXE goto havepy
echo.
echo No se pudo instalar Python automaticamente.
echo Descarga e instala "Python 3.12 Windows installer (64-bit)" desde:
echo   https://www.python.org/downloads/release/python-31210/
echo y vuelve a abrir run.bat.
pause
exit /b 1

:havepy
echo Usando Python: %PYEXE%
if exist .venv\instalado.txt goto run
if exist .venv rmdir /s /q .venv
echo Preparando ClipRadar por primera vez, tarda unos minutos...
%PYEXE% -m venv .venv
if errorlevel 1 goto fail
.venv\Scripts\python -m pip install --upgrade pip -q --no-cache-dir
.venv\Scripts\python -m pip install --no-cache-dir -r requirements.txt
if errorlevel 1 goto fail
echo ok> .venv\instalado.txt

:run
.venv\Scripts\python -m app
pause
exit /b 0

:fail
echo.
echo La instalacion fallo. Copia el texto de arriba y enviaselo a Claude.
pause
exit /b 1

:trypy
if defined PYEXE exit /b 0
py -%1 -c "%CHECK%" >nul 2>nul && set "PYEXE=py -%1"
exit /b 0

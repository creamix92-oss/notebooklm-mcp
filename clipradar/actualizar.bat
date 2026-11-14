@echo off
rem ClipRadar - descarga la ultima version y la copia encima (conserva clips, modelos e instalacion)
setlocal
cd /d "%~dp0"
echo Cierra la ventana de ClipRadar si esta abierta y pulsa una tecla para actualizar.
pause >nul
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; $z=Join-Path $env:TEMP 'clipradar_update.zip'; $d=Join-Path $env:TEMP 'clipradar_update'; Invoke-WebRequest -UseBasicParsing 'https://github.com/creamix92-oss/notebooklm-mcp/archive/refs/heads/ccr-69c3926a-c1bw3r.zip' -OutFile $z; if (Test-Path $d) { Remove-Item $d -Recurse -Force }; Expand-Archive $z $d; $src=Join-Path (Get-ChildItem $d -Directory)[0].FullName 'clipradar'; Copy-Item (Join-Path $src '*') '.' -Recurse -Force"
if errorlevel 1 (
  echo No se pudo actualizar. Revisa tu conexion a internet.
  pause
  exit /b 1
)
echo Actualizado. Abre run.bat para iniciar ClipRadar.
pause

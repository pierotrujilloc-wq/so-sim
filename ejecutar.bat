@echo off
setlocal
rem Usar el entorno del proyecto sin depender del PATH ni activarlo.
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo No se encontro el entorno .venv del proyecto.
    echo Consulta la seccion Ejecutar en Windows del README para crearlo.
    exit /b 1
)

"%~dp0.venv\Scripts\python.exe" -X utf8 "%~dp0python\main.py" %*
exit /b %errorlevel%

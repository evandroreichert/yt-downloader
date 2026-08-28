@echo off
setlocal
set "VENV_PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%VENV_PYTHON%" (
    echo Ambiente virtual nao encontrado. Execute instalar.bat primeiro.
    if not defined MEDIA_TOOLS_NO_PAUSE pause
    exit /b 1
)
"%VENV_PYTHON%" "%~dp0cli.py" %*
exit /b %ERRORLEVEL%

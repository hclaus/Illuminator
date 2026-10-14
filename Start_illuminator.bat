@echo off
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
    python ScreenV1.py
) else (
    py ScreenV1.py
)

if errorlevel 1 (
    echo.
    echo Illuminator exited with an error.
    pause
)

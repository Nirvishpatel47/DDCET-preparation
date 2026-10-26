
@echo off
title Gujarat DDCET Preparation System

echo ========================================================
echo  Starting Gujarat DDCET Exam Preparation Application
echo ========================================================
echo.

cd /d "%~dp0"

echo Project directory: %CD%
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Application stopped or failed to start.
pause

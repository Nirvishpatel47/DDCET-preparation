@echo off
echo ========================================================
echo  Starting Gujarat DDCET Exam Preparation Application
echo  Offline-First Mastery & Revision System
echo ========================================================
echo.
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
pause

#!/usr/bin/env bash
echo "========================================================"
echo " Starting Gujarat DDCET Exam Preparation Application"
echo " Offline-First Mastery & Revision System"
echo "========================================================"
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload

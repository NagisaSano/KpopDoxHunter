@echo off
REM Run KpopDoxHunter scan + dashboard

REM 1) Activate virtualenv (optional)
REM call .venv\Scripts\activate.bat

REM 2) Run ML scan
echo [KpopDoxHunter] Running ML scan...
python proto.py

REM 3) Start Flask dashboard
echo [KpopDoxHunter] Starting Flask dashboard...
python dashboard.py

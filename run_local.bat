@echo off
REM Windows-friendly script to run local controller and worker (no Docker)
python simulator\controller_app.py
start /B python simulator\worker_app.py
echo Controller and worker started. Use Ctrl+C to stop.

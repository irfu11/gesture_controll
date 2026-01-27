@echo off
REM Activate virtualenv and run the Flask app (Windows)
if exist .venv\Scripts\activate.bat (
  call .venv\Scripts\activate.bat
) else (
  echo Virtual environment not found. Create one with: python -m venv .venv
  pause
  exit /b 1
)
cd backend
%~dp0.venv\Scripts\python.exe app.py
pause

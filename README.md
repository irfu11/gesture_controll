# Coca-Cola Gesture System (Local Run)

This repository contains a small demo: a frontend using MediaPipe Hands to detect gestures and a Flask + Socket.IO backend that maps gestures to actions.

Quick start (Windows PowerShell):

1. Create & activate virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
pip install -r backend/requirements.txt
```

3. Run the backend

```powershell
python backend/app.py
```

4. Open the app

- Visit http://localhost:5000 in your browser
- Allow camera access
- Open DevTools Console to see gesture logs

Notes:
- The frontend already handles gesture detection and emits `gesture` events to the backend via Socket.IO.
- The backend maps gestures (pinch, fist, open_palm, thumbs_up, rotate, ice) to action names and emits `action` events back.
- For production you can run with Gunicorn + eventlet (Procfile already configured):

```
cd backend
python -m gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:8000 app:app
```

If you want, I can install the dependencies and start the server here to verify it — should I proceed?
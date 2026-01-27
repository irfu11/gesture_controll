Gesture Project

Overview
- Frontend (`frontend/index.html`) uses MediaPipe Hands (browser JS) to detect gestures and emits `gesture` events over socket.io.
- Backend (`backend/app.py`) runs a Flask + Socket.IO server that receives and broadcasts gestures. Server-side MediaPipe was disabled due to compatibility with Python 3.13; the project uses client-side detection now.

Quick setup (Windows)
1. Ensure you have Python 3.10/3.11 if you want server-side MediaPipe; otherwise Python 3.8+ works for this server.
2. From project root, create & activate a virtual environment (example using builtin venv):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # or Activate.bat for cmd
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

4. Run the server:

```powershell
cd backend
.\.venv\Scripts\python.exe app.py
```

5. Open the app in a Chromium-based browser: http://127.0.0.1:5000 and allow camera access.

Notes
- If you want full server-side MediaPipe, install Python 3.10/3.11, create a fresh venv with that Python, then `pip install mediapipe` and adapt `backend/app.py` to use the solutions API. I can automate that setup if you want.

Optimization Tips
- Prefer client-side detection (current setup) for lowest latency and CPU usage on server.
- Debounce gestures client-side (we added a 350ms debounce) and server-side (600ms) to avoid repeated actions.
- Reduce camera resolution or frame rate if you see high CPU usage: change the `Camera` width/height in `frontend/index.html`.
- Use `eventlet` or `gevent` with Flask-SocketIO in production; install `eventlet` and run the app with it for better concurrency.

Server-side MediaPipe setup (optional)
If you want the server to perform detection centrally, follow these steps:

1. Install Python 3.11 and create a venv:

```powershell
py -3.11 -m venv .venv311
.\.venv311\Scripts\Activate.ps1
```

2. Install dependencies and a compatible MediaPipe:

```powershell
pip install -r requirements.txt
pip install mediapipe==0.8.10
```

3. Update `backend/app.py` to enable the Solutions API path (it already contains a fallback branch); then run using the Python 3.11 interpreter:

```powershell
cd backend
..\.venv311\Scripts\python.exe app.py
```

If you'd like, I can create the Python 3.11 venv, install MediaPipe, and enable the Solutions API branch automatically. Which would you like me to do?

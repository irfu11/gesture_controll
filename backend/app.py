from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import logging
import os

# Use the standard threading async mode for local runs to avoid eventlet
# issues on some Windows/Python builds. For production with Gunicorn, the
# Procfile already configures eventlet workers.
_async_mode = "threading"

# ================== FLASK SETUP ==================
app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend"
)
# initialize Socket.IO with chosen async mode
socketio = SocketIO(app, cors_allowed_origins="*", async_mode=_async_mode, transports=["websocket", "polling"])

# ================== MEDIAPIPE SETUP ==================
# Note: Client-side gesture detection (in frontend) handles all gesture recognition.
# Server only receives and maps gestures to actions.

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

# ================== SOCKET EVENTS ==================
@socketio.on("gesture")
def handle_client_gesture(data):
    """Handle gesture strings sent from the client-side detector.
    Maps gestures to actions and emits `action` events back to the frontend.
    """
    print("Client gesture:", data)
    action = None
    # Mapping based on `gestures_rules.py`:
    # - pinch      -> open_coke (Fill bottle / Open Coke)
    # - fist       -> reset (Stop / Reset)
    # - open_palm  -> welcome (Idle / Welcome)
    # - thumbs_up  -> toggle_theme (Toggle Dark Mode)
    # - rotate     -> rotate_bottle (Rotate Bottle)
    # - ice        -> drop_ice (Drop Ice Cubes)
    # Keep `click` for legacy/select gestures from frontend
    if data == "pinch":
        action = "open_coke"
    elif data == "fist":
        action = "reset"
    elif data == "open_palm":
        action = "welcome"
    elif data == "thumbs_up":
        action = "toggle_theme"
    elif data == "rotate":
        action = "rotate_bottle"
    elif data == "ice" or data == "water":
        # Frontend emits 'water' for the water/drop gesture; keep backward compatibility
        action = "drop_ice"
    elif data == "click":
        action = "select"
    else:
        logging.info(f"Unmapped gesture received: {data}")

    if action:
        socketio.emit("action", action)

@socketio.on("connect")
def connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def disconnect():
    print("❌ Client disconnected")

# ================== RUN SERVER ==================
if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    # If SSL cert/key are provided we'll run on 8443 by default, otherwise 5000
    cert_path = os.environ.get("SSL_CERT")
    key_path = os.environ.get("SSL_KEY")
    if cert_path and key_path:
        port = int(os.environ.get("PORT", "8443"))
        ssl_context = (cert_path, key_path)
    else:
        port = int(os.environ.get("PORT", "5000"))
        ssl_context = None

    scheme = "https" if ssl_context else "http"
    logging.info(f"Starting server on {scheme}://{host}:{port} (async_mode={socketio.async_mode})")
    # Disable the Werkzeug reloader when running under Socket.IO to avoid
    # KeyError: 'WERKZEUG_SERVER_FD' on some Windows/Python combinations.
    # Passing `ssl_context` enables HTTPS when cert/key are set.
    socketio.run(
        app,
        host=host,
        port=port,
        debug=True,
        use_reloader=False,
        ssl_context=ssl_context,
    )

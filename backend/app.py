from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

# ================== FLASK SETUP ==================
app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend"
)
socketio = SocketIO(app, cors_allowed_origins="*", transports=["websocket", "polling"])

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

    if data == "thumbs_up" or data == "click":
        action = "select"
    elif data == "fist":
        action = "scroll_down"
    elif data == "open_palm":
        action = "scroll_up"
    elif data == "rock":
        action = "toggle_theme"

    if action:
        socketio.emit("action", action)

@socketio.on("connect")
def connect():
    print("✅ Client connected")

@socketio.on("disconnect")
def disconnect():
    print("❌ Client disconnected")


@socketio.on("gesture")
def handle_client_gesture(data):
    """Handle gesture strings sent from the client-side detector.
    Maps gestures to actions and emits `action` events back to the frontend.
    """
    print("Client gesture:", data)
    action = None

    if data == "thumbs_up" or data == "click":
        action = "select"
    elif data == "fist":
        action = "scroll_down"
    elif data == "open_palm":
        action = "scroll_up"
    elif data == "rock":
        action = "toggle_theme"

    if action:
        socketio.emit("action", action)

# ================== RUN SERVER ==================
if __name__ == "__main__":
    socketio.run(
        app,
        host="localhost",
        port=5000,
        debug=True
    )

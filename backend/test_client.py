from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import cv2
import base64
import numpy as np
import math
import os
import time

from gestures_rules import detect_gesture

# ================== FLASK SETUP ==================
app = Flask(
    __name__,
    template_folder="../frontend",
    static_folder="../frontend"
)
socketio = SocketIO(app, cors_allowed_origins="*")

# ================== MEDIAPIPE SETUP ==================
hands = None
prev_wrist_x = None

try:
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    import mediapipe as mp

    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "hand_landmarker.task")

    if not os.path.exists(model_path):
        import urllib.request
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
            model_path
        )

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=1)
    hands = vision.HandLandmarker.create_from_options(options)

    print("✅ Hand detection initialized")

except Exception as e:
    print("❌ MediaPipe failed:", e)

# ================== UTILS ==================
def dist(p1, p2):
    return math.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)

# ================== ROUTES ==================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})

# ================== SOCKET EVENTS ==================
@socketio.on("frame")
def process_frame(data):
    global prev_wrist_x

    img_bytes = base64.b64decode(data)
    npimg = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    gesture = "none"
    action = None

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    if hands and hasattr(hands, "detect"):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = hands.detect(mp_image)

        if result.hand_landmarks:
            hand = result.hand_landmarks[0]
            hand = [type("LM", (), {"x": p.x, "y": p.y, "z": 0})() for p in hand]

            # 👋 Detect base gesture
            gesture = detect_gesture(hand)

            # ================== GESTURE → ACTION ==================
            if gesture == "thumbs_up":
                action = "select"

            elif gesture == "fist":
                action = "scroll_down"

            elif gesture == "open_palm":
                action = "scroll_up"

            elif gesture == "rock":
                action = "toggle_theme"

    # 🔁 Emit to frontend
    socketio.emit("gesture", gesture)
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
    socketio.run(
        app,
        host="localhost",
        port=5000,
        debug=True
    )

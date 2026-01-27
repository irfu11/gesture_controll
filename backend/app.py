from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import cv2
import base64, numpy as np
import math
import os

from gestures_rules import detect_gesture
import time
from flask import request
from collections import defaultdict

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')
socketio = SocketIO(app, cors_allowed_origins="*")

# Hand detection setup with new MediaPipe API
hands = None
try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    import mediapipe as mp
    
    # Get the path to the hand landmarker model
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, 'hand_landmarker.task')
    
    # Download model if not exists
    if not os.path.exists(model_path):
        print("⏳ Hand landmarker model not found. Downloading...")
        import urllib.request
        model_url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
        try:
            urllib.request.urlretrieve(model_url, model_path)
            print("✅ Model downloaded successfully")
        except Exception as e:
            print(f"Failed to download model: {e}")
            model_path = None
    
    if model_path and os.path.exists(model_path):
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
        hands = vision.HandLandmarker.create_from_options(options)
        print("✅ Hand detection initialized with MediaPipe Tasks API")
    else:
        print("⚠️ Hand landmarker model not available")
except Exception as e:
    print(f"MediaPipe Tasks API failed: {e}")
    print("Attempting fallback to Solutions API...")
    
    # Fallback to old API if available
    try:
        import mediapipe as mp
        if hasattr(mp, 'solutions'):
            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                max_num_hands=2,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.7
            )
            print("✅ Using old MediaPipe Solutions API")
        else:
            print("⚠️ MediaPipe Solutions API not available - using motion detection fallback")
    except Exception as e2:
        print(f"Fallback failed: {e2}")

# Simple motion detection fallback
prev_frame = None

prev_wrist_x = None
prev_zoom_dist = None

def dist(p1, p2):
    """Calculate Euclidean distance between two points"""
    if hasattr(p1, 'x'):  # MediaPipe landmark format
        return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)
    else:  # tuple/list format
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})

@socketio.on("frame")
def process_frame(data):
    """Process incoming video frame and detect gestures"""
    global prev_wrist_x, prev_zoom_dist, prev_frame

    try:
        img_bytes = base64.b64decode(data)
        npimg = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        gesture = "none"
        
        # Process frame with hand detection if available
        if hands is not None:
            try:
                # Convert BGR to RGB
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Check if using new API (HandLandmarker) or old API (Hands)
                if hasattr(hands, 'detect'):
                    # New MediaPipe Tasks API
                    import mediapipe as mp
                    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                    detection_result = hands.detect(mp_image)
                    
                    if detection_result.hand_landmarks and len(detection_result.hand_landmarks) > 0:
                        hand_landmarks = detection_result.hand_landmarks[0]
                        # Convert to list of objects with x, y attributes
                        hand = [type('Landmark', (), {'x': lm.x, 'y': lm.y, 'z': getattr(lm, 'z', 0)})() for lm in hand_landmarks]
                        
                        gesture = detect_gesture(hand)
                        
                        # 🤏 CLICK (PINCH)
                        if dist(hand[4], hand[8]) < 0.03:
                            gesture = "click"
                        
                        # 👉👈 SWIPE
                        wrist = hand[0]
                        if prev_wrist_x is not None:
                            dx = wrist.x - prev_wrist_x
                            if dx > 0.08:
                                gesture = "next"
                            elif dx < -0.08:
                                gesture = "prev"
                        prev_wrist_x = wrist.x
                        
                        # 🔍 ZOOM (TWO HANDS)
                        if len(detection_result.hand_landmarks) == 2:
                            h1_landmarks = detection_result.hand_landmarks[0]
                            h2_landmarks = detection_result.hand_landmarks[1]
                            h1 = [type('Landmark', (), {'x': lm.x, 'y': lm.y, 'z': getattr(lm, 'z', 0)})() for lm in h1_landmarks]
                            h2 = [type('Landmark', (), {'x': lm.x, 'y': lm.y, 'z': getattr(lm, 'z', 0)})() for lm in h2_landmarks]
                            d = dist(h1[0], h2[0])
                            
                            if prev_zoom_dist is not None:
                                if d > prev_zoom_dist + 0.02:
                                    gesture = "zoom_in"
                                elif d < prev_zoom_dist - 0.02:
                                    gesture = "zoom_out"
                            
                            prev_zoom_dist = d
                        else:
                            prev_zoom_dist = None
                else:
                    # Old MediaPipe Solutions API
                    results = hands.process(rgb)
                    
                    if results.multi_hand_landmarks:
                        hand = results.multi_hand_landmarks[0].landmark
                        
                        gesture = detect_gesture(hand)
                        
                        # 🤏 CLICK (PINCH)
                        if dist(hand[4], hand[8]) < 0.03:
                            gesture = "click"
                        
                        # 👉👈 SWIPE
                        wrist = hand[0]
                        if prev_wrist_x is not None:
                            dx = wrist.x - prev_wrist_x
                            if dx > 0.08:
                                gesture = "next"
                            elif dx < -0.08:
                                gesture = "prev"
                        prev_wrist_x = wrist.x
                        
                        # 🔍 ZOOM (TWO HANDS)
                        if len(results.multi_hand_landmarks) == 2:
                            h1 = results.multi_hand_landmarks[0].landmark
                            h2 = results.multi_hand_landmarks[1].landmark
                            d = dist(h1[0], h2[0])
                            
                            if prev_zoom_dist is not None:
                                if d > prev_zoom_dist + 0.02:
                                    gesture = "zoom_in"
                                elif d < prev_zoom_dist - 0.02:
                                    gesture = "zoom_out"
                            
                            prev_zoom_dist = d
                        else:
                            prev_zoom_dist = None
            except Exception as e:
                print(f"Error in hand detection: {e}")
        else:
            # Fallback: Motion detection
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.blur(gray, (5, 5))
                
                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, gray)
                    motion_score = np.sum(diff) / (frame.shape[0] * frame.shape[1] * 255)
                    
                    # Simple motion-based gesture detection
                    if motion_score > 0.2:
                        gesture = "motion"
                
                prev_frame = gray
            except Exception as e:
                print(f"Error in motion detection: {e}")

        socketio.emit("gesture", gesture)
    except Exception as e:
        print(f"Error processing frame: {e}")

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('response', {'data': 'Connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


# Accept gestures emitted from the frontend (client-side detection)
@socketio.on('gesture')
def handle_gesture(data):
    """Receive gesture from a client, debounce and broadcast to all clients."""
    try:
        gesture = data if isinstance(data, str) else (data.get('gesture') if isinstance(data, dict) else str(data))
    except Exception:
        gesture = 'unknown'

    sid = None
    try:
        sid = request.sid
    except Exception:
        sid = 'unknown'

    now_ms = int(time.time() * 1000)
    # per-sid last gesture tracking
    if not hasattr(handle_gesture, 'last_by_sid'):
        handle_gesture.last_by_sid = defaultdict(lambda: {'gesture': None, 'ts': 0})

    last = handle_gesture.last_by_sid[sid]
    DEBOUNCE_MS = 600
    # ignore repeated same gesture within debounce window
    if last['gesture'] == gesture and (now_ms - last['ts']) < DEBOUNCE_MS:
        return

    # update last
    handle_gesture.last_by_sid[sid] = {'gesture': gesture, 'ts': now_ms}

    print(f"Received gesture from client (sid={sid}): {gesture}")

    # Map gestures to higher-level actions (server-side broadcast)
    action = None
    if gesture == 'open_palm':
        action = 'scroll_down'
    elif gesture == 'fist':
        action = 'stop'
    elif gesture == 'victory':
        action = 'scroll_up'
    elif gesture == 'thumbs_up':
        action = 'highlight'
    elif gesture == 'rock':
        action = 'toggle_dark'
    elif gesture == 'click':
        action = 'click_center'

    # broadcast both raw gesture and mapped action
    socketio.emit('gesture', gesture)
    if action:
        socketio.emit('action', {'action': action, 'source_sid': sid})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)

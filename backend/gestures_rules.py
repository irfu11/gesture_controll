"""
gesture_rule.py
----------------
Rule-based gesture detection for Coca-Cola Gesture System
Uses MediaPipe Hands landmarks (21 points)

Gestures Supported:
- pinch      -> Fill bottle / Open Coke
- fist       -> Stop / Reset
- open_palm  -> Idle / Welcome
- thumbs_up  -> Toggle Dark Mode
- rotate     -> Rotate Bottle
- ice        -> Drop Ice Cubes
"""

import time

# ================== CONFIG ==================
PINCH_THRESHOLD = 0.05       # Thumb–Index distance
DEBOUNCE_TIME = 0.4          # seconds


# ================== HELPERS ==================
def finger_open(tip, mcp):
    """
    Returns True if finger is open.
    MediaPipe y-axis is inverted.
    """
    return tip.y < mcp.y


def distance(p1, p2):
    """
    Euclidean distance in normalized coordinates
    """
    return ((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2) ** 0.5


# ================== GESTURE DETECTOR ==================
_last_gesture = None
_last_time = 0


def detect_gesture(hand_landmarks):
    """
    Input:
        hand_landmarks -> list of 21 MediaPipe landmarks
    Output:
        gesture string
    """

    global _last_gesture, _last_time

    # -------- Finger states --------
    thumb = finger_open(hand_landmarks[4], hand_landmarks[2])
    index = finger_open(hand_landmarks[8], hand_landmarks[5])
    middle = finger_open(hand_landmarks[12], hand_landmarks[9])
    ring = finger_open(hand_landmarks[16], hand_landmarks[13])
    pinky = finger_open(hand_landmarks[20], hand_landmarks[17])

    # -------- Pinch Detection (PRIORITY) --------
    thumb_index_dist = distance(hand_landmarks[4], hand_landmarks[8])
    if thumb_index_dist < PINCH_THRESHOLD:
        gesture = "pinch"
    else:
        # -------- Fist --------
        if not any([thumb, index, middle, ring, pinky]):
            gesture = "fist"

        # -------- Open Palm --------
        elif all([thumb, index, middle, ring, pinky]):
            gesture = "open_palm"

        # -------- Thumbs Up --------
        elif thumb and not any([index, middle, ring, pinky]):
            gesture = "thumbs_up"

        # -------- Rotate Bottle (Victory) --------
        elif index and middle and not ring and not pinky:
            gesture = "rotate"

        # -------- Drop Ice Cubes (Rock) --------
        elif index and pinky and not middle and not ring:
            gesture = "ice"

        else:
            gesture = "none"

    # -------- Debounce Logic --------
    now = time.time()
    if gesture == _last_gesture and (now - _last_time) < DEBOUNCE_TIME:
        return None

    _last_gesture = gesture
    _last_time = now

    return gesture

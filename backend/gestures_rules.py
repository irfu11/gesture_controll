def finger_open(tip, mcp):
    return tip.y < mcp.y   # y-axis inverted in MediaPipe

def detect_gesture(hand):
    thumb = finger_open(hand[4], hand[2])
    index = finger_open(hand[8], hand[5])
    middle = finger_open(hand[12], hand[9])
    ring = finger_open(hand[16], hand[13])
    pinky = finger_open(hand[20], hand[17])

    # ✊ FIST
    if not any([thumb, index, middle, ring, pinky]):
        return "fist"

    # ✋ OPEN PALM
    if all([thumb, index, middle, ring, pinky]):
        return "open_palm"

    # 👍 THUMBS UP
    if thumb and not any([index, middle, ring, pinky]):
        return "thumbs_up"

    # ✌ VICTORY
    if index and middle and not ring and not pinky:
        return "victory"

    # 🤘 ROCK
    if index and pinky and not middle and not ring:
        return "rock"

    return "none"

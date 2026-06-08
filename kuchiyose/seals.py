"""
Gesture detection logic for each seal in the Kuchiyose no Jutsu sequence.

Landmark indices:
  0  = WRIST
  1-4   = Thumb  (CMC, MCP, IP, TIP)
  5-8   = Index  (MCP, PIP, DIP, TIP)
  9-12  = Middle (MCP, PIP, DIP, TIP)
  13-16 = Ring   (MCP, PIP, DIP, TIP)
  17-20 = Pinky  (MCP, PIP, DIP, TIP)
"""

# (TIP_idx, PIP_idx) for each non-thumb finger
FINGER_JOINTS = {
    "index":  (8,  6),
    "middle": (12, 10),
    "ring":   (16, 14),
    "pinky":  (20, 18),
}


def _finger_extended(lm, tip, pip):
    """True when TIP is above PIP (y decreases upward in normalized coords)."""
    return lm[tip][1] < lm[pip][1]


def _thumb_extended(lm):
    """Thumb TIP further from palm center than Thumb MCP on x-axis."""
    tip_x = lm[4][0]
    mcp_x = lm[2][0]
    # Works for both left and right hand by checking relative distance from wrist
    wrist_x = lm[0][0]
    return abs(tip_x - wrist_x) > abs(mcp_x - wrist_x)


def detect_bite(lm, frame_h=None):
    """State 0 — index finger raised above face (y < 0.4)."""
    index_extended = _finger_extended(lm, 8, 6)
    index_high = lm[8][1] < 0.4
    return index_extended and index_high


def detect_pig(lm, frame_h=None):
    """State 1 — PIG: full fist, all fingers curled."""
    for tip, pip in FINGER_JOINTS.values():
        if _finger_extended(lm, tip, pip):
            return False
    # Thumb tip close to thumb base (landmark 2)
    thumb_tip = lm[4]
    thumb_base = lm[2]
    dist = abs(thumb_tip[0] - thumb_base[0]) + abs(thumb_tip[1] - thumb_base[1])
    return dist < 0.15


def detect_dog(lm, frame_h=None):
    """State 2 — DOG: index + pinky extended, middle + ring curled."""
    index_ext = _finger_extended(lm, 8, 6)
    pinky_ext = _finger_extended(lm, 20, 18)
    middle_curl = not _finger_extended(lm, 12, 10)
    ring_curl = not _finger_extended(lm, 16, 14)
    return index_ext and pinky_ext and middle_curl and ring_curl


def detect_rooster(lm, frame_h=None):
    """State 3 — ROOSTER: thumb + index + middle extended, ring + pinky curled."""
    thumb_ext = _thumb_extended(lm)
    index_ext = _finger_extended(lm, 8, 6)
    middle_ext = _finger_extended(lm, 12, 10)
    ring_curl = not _finger_extended(lm, 16, 14)
    pinky_curl = not _finger_extended(lm, 20, 18)
    return thumb_ext and index_ext and middle_ext and ring_curl and pinky_curl


def detect_monkey(lm, frame_h=None):
    """State 4 — MONKEY: all extended except ring curled."""
    thumb_ext = _thumb_extended(lm)
    index_ext = _finger_extended(lm, 8, 6)
    middle_ext = _finger_extended(lm, 12, 10)
    ring_curl = not _finger_extended(lm, 16, 14)
    pinky_ext = _finger_extended(lm, 20, 18)
    return thumb_ext and index_ext and middle_ext and ring_curl and pinky_ext


def detect_ram(lm, frame_h=None):
    """State 5 — RAM: only middle + ring extended."""
    index_curl = not _finger_extended(lm, 8, 6)
    middle_ext = _finger_extended(lm, 12, 10)
    ring_ext = _finger_extended(lm, 16, 14)
    pinky_curl = not _finger_extended(lm, 20, 18)
    thumb_curl = not _thumb_extended(lm)
    return index_curl and middle_ext and ring_ext and pinky_curl and thumb_curl


def detect_ground(lm, frame_h=None):
    """State 6 — GROUND: all fingers extended, hand held flat/horizontal."""
    thumb_ext = _thumb_extended(lm)
    index_ext = _finger_extended(lm, 8, 6)
    middle_ext = _finger_extended(lm, 12, 10)
    ring_ext = _finger_extended(lm, 16, 14)
    pinky_ext = _finger_extended(lm, 20, 18)
    all_ext = thumb_ext and index_ext and middle_ext and ring_ext and pinky_ext

    # Flat hand: wrist and middle-MCP close in y
    dy = abs(lm[0][1] - lm[9][1])
    flat = dy < 0.25

    return all_ext and flat


SEAL_DETECTORS = [
    detect_bite,
    detect_pig,
    detect_dog,
    detect_rooster,
    detect_monkey,
    detect_ram,
    detect_ground,
]

SEAL_NAMES = [
    "Morder o Dedo (BITE)",
    "Porco — PIG",
    "Cachorro — DOG",
    "Galo — ROOSTER",
    "Macaco — MONKEY",
    "Ovelha — RAM",
    "Palma no Chão — GROUND",
]

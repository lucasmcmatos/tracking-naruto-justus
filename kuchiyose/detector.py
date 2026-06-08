import cv2
import mediapipe as mp
import numpy as np


class HandDetector:
    def __init__(self, min_detection_confidence=0.7, min_tracking_confidence=0.5):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

        self.last_confidence = 0.0

    def process(self, frame_bgr):
        """Process a BGR frame and return landmarks or None."""
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        frame_rgb.flags.writeable = False
        results = self.hands.process(frame_rgb)
        frame_rgb.flags.writeable = True

        if not results.multi_hand_landmarks:
            self.last_confidence = 0.0
            return None, None

        hand_landmarks = results.multi_hand_landmarks[0]

        if results.multi_handedness:
            self.last_confidence = results.multi_handedness[0].classification[0].score
        else:
            self.last_confidence = 1.0

        return hand_landmarks, results

    def draw(self, frame_bgr, hand_landmarks):
        """Draw landmarks and connections onto frame in place."""
        self.mp_drawing.draw_landmarks(
            frame_bgr,
            hand_landmarks,
            self.mp_hands.HAND_CONNECTIONS,
            self.mp_drawing_styles.get_default_hand_landmarks_style(),
            self.mp_drawing_styles.get_default_hand_connections_style(),
        )

    def get_landmark_list(self, hand_landmarks, frame_w, frame_h):
        """Return list of (x_norm, y_norm, z_norm) for all 21 landmarks."""
        lm = hand_landmarks.landmark
        return [(p.x, p.y, p.z) for p in lm]

    def close(self):
        self.hands.close()

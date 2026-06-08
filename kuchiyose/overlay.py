import cv2
import numpy as np
import time


_ORANGE = (0, 140, 255)
_GREEN  = (0, 220, 80)
_WHITE  = (255, 255, 255)
_RED    = (0, 0, 220)
_YELLOW = (0, 220, 220)
_BLACK  = (0, 0, 0)


def draw_hud(frame, state, total, consecutive, confirm_frames,
             current_name, next_name, fps, confidence):
    h, w = frame.shape[:2]

    # --- progress bar ---
    bar_filled = "■" * state
    bar_empty  = "□" * (total - state)
    bar_text   = f"[{bar_filled}{bar_empty}]"
    cv2.putText(frame, bar_text, (10, 30),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, _ORANGE, 2, cv2.LINE_AA)

    # --- current gesture ---
    cv2.putText(frame, f"Gesto: {current_name}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, _WHITE, 1, cv2.LINE_AA)

    # --- next gesture ---
    cv2.putText(frame, f"Proximo: {next_name}", (10, 85),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, _YELLOW, 1, cv2.LINE_AA)

    # --- confirm progress micro-bar ---
    bar_w = 120
    ratio = min(consecutive / max(confirm_frames, 1), 1.0)
    cv2.rectangle(frame, (10, 95), (10 + bar_w, 108), (60, 60, 60), -1)
    cv2.rectangle(frame, (10, 95), (10 + int(bar_w * ratio), 108), _GREEN, -1)
    cv2.rectangle(frame, (10, 95), (10 + bar_w, 108), _WHITE, 1)

    # --- metrics ---
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 130, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, _WHITE, 1, cv2.LINE_AA)
    cv2.putText(frame, f"Conf: {confidence:.2f}", (w - 130, 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, _WHITE, 1, cv2.LINE_AA)
    cv2.putText(frame, f"Estado: {state}/{total}", (w - 130, 71),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, _WHITE, 1, cv2.LINE_AA)


def draw_completion(frame, start_time, jutsu_name=""):
    """Pulsing red overlay + animated KUCHIYOSE NO JUTSU! text + jutsu name."""
    elapsed = time.time() - start_time
    pulse = abs(np.sin(elapsed * 3)) * 0.35 + 0.15
    tint = np.zeros_like(frame, dtype=np.uint8)
    tint[:] = (0, 0, 180)
    cv2.addWeighted(tint, pulse, frame, 1 - pulse, 0, frame)

    h, w = frame.shape[:2]
    text = "KUCHIYOSE NO JUTSU!"
    scale = 1.0 + 0.15 * abs(np.sin(elapsed * 2))
    thickness = 3
    (tw, _th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, scale, thickness)
    x = (w - tw) // 2
    y = h // 2 - 30

    cv2.putText(frame, text, (x + 3, y + 3),
                cv2.FONT_HERSHEY_DUPLEX, scale, _BLACK, thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y),
                cv2.FONT_HERSHEY_DUPLEX, scale, _ORANGE, thickness, cv2.LINE_AA)

    if jutsu_name:
        (jw, _), _ = cv2.getTextSize(jutsu_name, cv2.FONT_HERSHEY_DUPLEX, 0.9, 2)
        jx = (w - jw) // 2
        cv2.putText(frame, jutsu_name, (jx + 2, y + 52),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, _BLACK, 4, cv2.LINE_AA)
        cv2.putText(frame, jutsu_name, (jx, y + 50),
                    cv2.FONT_HERSHEY_DUPLEX, 0.9, _YELLOW, 2, cv2.LINE_AA)

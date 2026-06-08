import time
from seals import SEAL_DETECTORS, SEAL_NAMES

CONFIRM_FRAMES = 15   # frames consecutivos para confirmar gesto
TIMEOUT_SECS = 8.0    # tempo máximo sem avançar antes de resetar
FINISH_HOLD = 3.0     # segundos mostrando efeito final antes de resetar


class StateMachine:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.state = 0          # 0..6 = selando, 7 = invocação completa
        self.consecutive = 0
        self.last_advance = time.time()
        self.finish_time = None
        self.gesture_times = []  # tempo para confirmar cada gesto
        self._gesture_start = time.time()

    @property
    def total_seals(self):
        return len(SEAL_DETECTORS)

    @property
    def current_seal_name(self):
        if self.state >= self.total_seals:
            return "KUCHIYOSE NO JUTSU!"
        return SEAL_NAMES[self.state]

    @property
    def next_seal_name(self):
        nxt = self.state + 1
        if nxt >= self.total_seals:
            return "—"
        return SEAL_NAMES[nxt]

    @property
    def is_complete(self):
        return self.state >= self.total_seals

    def update(self, lm):
        """Feed current landmarks, return True if a new seal was confirmed."""
        now = time.time()

        # After completion hold, auto-reset
        if self.is_complete:
            if self.finish_time and (now - self.finish_time) > FINISH_HOLD:
                self._reset()
            return False

        # Timeout check
        if (now - self.last_advance) > TIMEOUT_SECS:
            self._reset()
            return False

        if lm is None:
            self.consecutive = 0
            return False

        detector = SEAL_DETECTORS[self.state]
        if detector(lm):
            self.consecutive += 1
        else:
            self.consecutive = 0

        if self.consecutive >= CONFIRM_FRAMES:
            elapsed = now - self._gesture_start
            self.gesture_times.append(elapsed)
            self.state += 1
            self.consecutive = 0
            self.last_advance = now
            self._gesture_start = now
            if self.is_complete:
                self.finish_time = now
            return True

        return False

    def progress(self):
        """Return (current_state, total_seals, consecutive, confirm_frames)."""
        return self.state, self.total_seals, self.consecutive, CONFIRM_FRAMES

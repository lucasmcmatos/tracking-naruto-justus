import time
import cv2


class Metrics:
    def __init__(self):
        self.start_time = time.time()
        self.frame_count = 0
        self.confidence_sum = 0.0
        self.confidence_samples = 0
        self._last_fps_time = time.time()
        self._fps_frame_count = 0
        self.current_fps = 0.0

    def update(self, confidence):
        self.frame_count += 1
        self._fps_frame_count += 1
        if confidence > 0:
            self.confidence_sum += confidence
            self.confidence_samples += 1

        now = time.time()
        elapsed = now - self._last_fps_time
        if elapsed >= 0.5:
            self.current_fps = self._fps_frame_count / elapsed
            self._fps_frame_count = 0
            self._last_fps_time = now

    @property
    def avg_confidence(self):
        if self.confidence_samples == 0:
            return 0.0
        return self.confidence_sum / self.confidence_samples

    @property
    def elapsed(self):
        return time.time() - self.start_time

    def print_summary(self, gesture_times):
        total = self.elapsed
        fps_avg = self.frame_count / total if total > 0 else 0
        print("\n========== METRICAS FINAIS ==========")
        print(f"Frames totais    : {self.frame_count}")
        print(f"FPS medio        : {fps_avg:.2f}")
        print(f"Confianca media  : {self.avg_confidence:.3f}")
        print(f"Tempo total      : {total:.1f}s")
        if gesture_times:
            print("\nTempo por gesto:")
            labels = ["BITE", "PIG", "DOG", "ROOSTER", "MONKEY", "RAM", "GROUND"]
            for i, t in enumerate(gesture_times):
                lbl = labels[i] if i < len(labels) else f"#{i}"
                print(f"  {lbl:10s}: {t:.2f}s")
        print("=====================================\n")

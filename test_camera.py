"""Diagnóstico completo da webcam — rode no terminal com: python test_camera.py"""
import cv2
import numpy as np

DEVICES = ["/dev/video0", "/dev/video1", 0, 1]
FORMATS = [
    ("YUYV", cv2.VideoWriter_fourcc(*"YUYV")),
    ("MJPG", cv2.VideoWriter_fourcc(*"MJPG")),
    (None,   None),  # sem forçar formato
]
WARMUP = 10  # frames descartados antes de avaliar


def test(src, fmt_name, fourcc):
    cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
    if not cap.isOpened():
        cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        return f"  NAO ABRIU"

    if fourcc is not None:
        cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    for _ in range(WARMUP):
        cap.read()

    ret, frame = cap.read()
    cap.release()

    if not ret or frame is None:
        return "  ret=False / frame=None"

    nonzero = int(np.count_nonzero(frame))
    mean = float(frame.mean())
    return f"  ret=True shape={frame.shape} mean={mean:.1f} nonzero={nonzero}"


print("=== Diagnóstico de câmera ===\n")
for src in DEVICES:
    print(f"--- Fonte: {src} ---")
    for fmt_name, fourcc in FORMATS:
        label = fmt_name if fmt_name else "DEFAULT"
        result = test(src, fmt_name, fourcc)
        print(f"  [{label}]{result}")
    print()

# Tenta capturar e salvar um frame para inspeção visual
print("--- Tentando salvar frame de diagnóstico ---")
for src in DEVICES:
    for fmt_name, fourcc in FORMATS:
        cap = cv2.VideoCapture(src, cv2.CAP_V4L2)
        if not cap.isOpened():
            cap = cv2.VideoCapture(src)
        if not cap.isOpened():
            continue
        if fourcc:
            cap.set(cv2.CAP_PROP_FOURCC, fourcc)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        for _ in range(WARMUP):
            cap.read()
        ret, frame = cap.read()
        cap.release()
        if ret and frame is not None and frame.mean() > 1.0:
            path = f"diag_{str(src).replace('/', '_')}_{fmt_name or 'DEFAULT'}.png"
            cv2.imwrite(path, frame)
            print(f"  Salvo: {path} (src={src} fmt={fmt_name or 'DEFAULT'})")
            break

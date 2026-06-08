"""
Kuchiyose no Jutsu — Reconhecimento de selos de mao em tempo real.
Rodar no Windows nativo (Python do Windows) para acesso a webcam e display.

  python main.py               # usa webcam 0
  python main.py --source 1    # outra camera
  python main.py --source video.mp4  # arquivo de video
"""

import argparse
import sys
import cv2

from detector import HandDetector
from state_machine import StateMachine
from overlay import draw_hud, draw_completion
from metrics import Metrics


JUTSUS = {
    "gamabunta": "Gamabunta — O Grande Sapo!",
    "katsuyu":   "Katsuyu — A Grande Lesma!",
    "manda":     "Manda — A Grande Serpente!",
    "gamakichi": "Gamakichi — O Sapo de Naruto!",
    "enma":      "Enma — O Rei dos Macacos!",
}


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--source", default="0",
                   help="Indice da webcam (0,1,...) ou caminho de arquivo de video")
    p.add_argument("--output", default="",
                   help="Salvar video de saida neste arquivo (ex: saida.avi)")
    p.add_argument("--width", type=int, default=640)
    p.add_argument("--height", type=int, default=480)
    p.add_argument("--jutsu", default="gamabunta",
                   choices=list(JUTSUS.keys()),
                   help="Jutsu a invocar: " + ", ".join(JUTSUS.keys()))
    return p.parse_args()


def open_capture(source, width, height):
    src = int(source) if source.isdigit() else source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        print(f"[ERRO] Nao foi possivel abrir a fonte: {source}")
        sys.exit(1)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    # descarta frames iniciais pretos enquanto a camera inicializa
    for _ in range(15):
        cap.read()
    return cap


def main():
    args = parse_args()

    cap = open_capture(args.source, args.width, args.height)
    detector = HandDetector()
    sm = StateMachine()
    metrics = Metrics()

    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        writer = cv2.VideoWriter(args.output, fourcc, 30,
                                 (args.width, args.height))

    win = "Kuchiyose no Jutsu — Pose Estimation"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, args.width, args.height)

    print("Pressione Q para sair.")
    print("Realize os 7 selos na ordem correta para invocar!")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (args.width, args.height))
        frame = cv2.flip(frame, 1)  # espelho — mais natural para o usuario

        hand_lm, results = detector.process(frame)

        lm_list = None
        if hand_lm is not None:
            detector.draw(frame, hand_lm)
            lm_list = detector.get_landmark_list(hand_lm, args.width, args.height)

        sm.update(lm_list)
        metrics.update(detector.last_confidence)

        state, total, consecutive, confirm_frames = sm.progress()

        if sm.is_complete:
            draw_completion(frame, sm.finish_time, JUTSUS[args.jutsu])
        else:
            draw_hud(
                frame,
                state=state,
                total=total,
                consecutive=consecutive,
                confirm_frames=confirm_frames,
                current_name=sm.current_seal_name,
                next_name=sm.next_seal_name,
                fps=metrics.current_fps,
                confidence=detector.last_confidence,
            )

        if writer:
            writer.write(frame)

        cv2.imshow(win, frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == 27:
            break

    metrics.print_summary(sm.gesture_times)

    cap.release()
    if writer:
        writer.release()
    detector.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

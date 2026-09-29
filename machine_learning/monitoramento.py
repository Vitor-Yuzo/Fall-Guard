import cv2
import time
from collections import deque
from ultralytics import YOLO


# =========================
# CONFIGURAÇÕES
# =========================

MODEL_PATH = "runs/detect/runs/fallguard_v1-6/weights/best.pt"

CONFIDENCE = 0.5
CAMERA_INDEX = 0

HISTORY_SIZE = 30
FALL_WINDOW_SECONDS = 5.0
COOLDOWN_SECONDS = 5.0


# =========================
# CARREGAMENTO DO MODELO
# =========================

model = YOLO(MODEL_PATH)

state_history = deque(maxlen=HISTORY_SIZE)

last_fall_time = 0
last_state = None


# =========================
# REGISTRA ESTADO
# =========================

def register_state(state):

    state_history.append({
        "state": state,
        "time": time.time()
    })


# =========================
# DETECÇÃO DE QUEDA
# =========================

def detect_fall():

    if len(state_history) < 2:
        return False

    states = list(state_history)

    # Procura o último stand
    last_stand = None

    for item in reversed(states):

        if item["state"] == "stand":
            last_stand = item
            break

    if last_stand is None:
        return False

    # Procura um lie depois do stand
    for item in states:

        if (
            item["state"] == "lie"
            and item["time"] > last_stand["time"]
        ):

            elapsed = item["time"] - last_stand["time"]

            if elapsed <= FALL_WINDOW_SECONDS:
                return True

    return False


# =========================
# WEBCAM
# =========================

cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():

    print("Erro: não foi possível abrir a webcam.")
    exit()


print("FallGuard iniciado.")
print("Pressione 'q' para sair.")


# =========================
# LOOP PRINCIPAL
# =========================

while True:

    ret, frame = cap.read()

    if not ret:

        print("Erro ao capturar frame.")
        break


    # =========================
    # YOLO
    # =========================

    results = model(
        frame,
        conf=CONFIDENCE,
        verbose=False
    )

    detected_state = None


    # =========================
    # ANALISA DETECÇÕES
    # =========================

    for result in results:

        boxes = result.boxes

        if boxes is None:
            continue

        for box in boxes:

            confidence = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            # Guarda o estado detectado
            detected_state = class_name

            # Coordenadas
            x1, y1, x2, y2 = map(
                int,
                box.xyxy[0]
            )

            # Bounding box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (255, 255, 255),
                2
            )

            # Label
            label = f"{class_name} {confidence:.2f}"

            cv2.putText(
                frame,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )


    # =========================
    # REGISTRA MUDANÇA DE ESTADO
    # =========================

    if detected_state is not None:

        if detected_state != last_state:

            register_state(detected_state)

            last_state = detected_state

            print(
                f"Estado alterado: {detected_state}"
            )


    # =========================
    # ANALISA QUEDA
    # =========================

    fall_detected = False

    if detected_state is not None:

        current_time = time.time()

        if (
            current_time - last_fall_time
            > COOLDOWN_SECONDS
        ):

            if detect_fall():

                fall_detected = True

                last_fall_time = current_time

                print(
                    "🚨 QUEDA DETECTADA!"
                )


    # =========================
    # INTERFACE
    # =========================

    if fall_detected:

        cv2.putText(
            frame,
            "QUEDA DETECTADA!",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.2,
            (255, 255, 255),
            3
        )

    else:

        status = (
            detected_state
            if detected_state
            else "Nenhuma pessoa detectada"
        )

        cv2.putText(
            frame,
            f"Estado: {status}",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2
        )


    # =========================
    # MOSTRA WEBCAM
    # =========================

    cv2.imshow(
        "FallGuard - Monitoramento",
        frame
    )


    # =========================
    # SAIR
    # =========================

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


# =========================
# FINALIZAÇÃO
# =========================

cap.release()
cv2.destroyAllWindows()

print("FallGuard encerrado.")
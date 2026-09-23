from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data="machine_learning/dataset/data.yaml",
    epochs=20,
    imgsz=640,
    batch=16,
    project="runs",
    name="fallguard_v1"
)
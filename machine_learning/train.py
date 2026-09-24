from ultralytics import YOLO

def main():
    model = YOLO("yolov8n.pt")

    model.train(
        data="machine_learning/dataset/data.yaml",
        epochs=20,
        imgsz=640,
        batch=16,
        device=0,
        project="runs",
        name="fallguard_v1"
    )

if __name__ == "__main__":
    main()
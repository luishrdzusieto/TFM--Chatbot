from ultralytics import YOLO

def detectar_componentes(img_path):
    model = YOLO("best.pt")
    results = model(source=img_path)
    detected_classes = []
    for result in results:
        for box in result.boxes.data:
            class_id = int(box[5])
            detected_classes.append(model.names[class_id])
    return list(set(detected_classes))

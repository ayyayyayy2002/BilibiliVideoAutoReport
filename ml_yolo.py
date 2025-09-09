import numpy as np
import cv2
from ml_load import load_yolo


def pad_top_left(img, target_w=640, target_h=640):
    canvas = np.ones((target_h, target_w, 3), dtype=np.uint8) * 114
    h, w = img.shape[:2]
    canvas[:h, :w] = img
    return canvas


def preprocess(img):
    img = img.astype(np.float32) / 255.0
    img = np.transpose(img, (2, 0, 1))  # HWC -> CHW
    return np.expand_dims(img, axis=0)  # NCHW


def iou(a, b):
    x1 = max(a["x"] - a["w"] / 2, b["x"] - b["w"] / 2)
    y1 = max(a["y"] - a["h"] / 2, b["y"] - b["h"] / 2)
    x2 = min(a["x"] + a["w"] / 2, b["x"] + b["w"] / 2)
    y2 = min(a["y"] + a["h"] / 2, b["y"] + b["h"] / 2)
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    union = a["w"] * a["h"] + b["w"] * b["h"] - inter
    return inter / union if union > 0 else 0


def nms(detections, iou_th):
    detections = sorted(detections, key=lambda d: d["conf"], reverse=True)
    keep = []
    used = [False] * len(detections)
    for i, a in enumerate(detections):
        if used[i]:
            continue
        keep.append(a)
        for j in range(i + 1, len(detections)):
            if used[j]:
                continue
            if a["class_id"] == detections[j]["class_id"] and iou(a, detections[j]) > iou_th:
                used[j] = True
    return keep


# ===== 模型加载与推理 =====
def run_yolo(img,YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS):

    img = pad_top_left(img, 640, 640)
    data = preprocess(img)

    # 推理
    preds = YOLO_MODEL.run([YOLO_OUTPUTS], {YOLO_INPUTS: data})[0]  # shape (1, 25200, 7)
    preds = preds[0]

    detections = []
    conf_th = 0.4
    for x, y, w, h, conf, class0, class1 in preds:
        if conf < conf_th:
            continue
        class_id = 0 if class0 >= class1 else 1
        detections.append({
            "x": float(x),
            "y": float(y),
            "w": float(w),
            "h": float(h),
            "conf": float(conf),
            "class_id": class_id
        })

    detections = nms(detections, 0.5)
    classA = [d for d in detections if d["class_id"] == 0]
    classB = [d for d in detections if d["class_id"] == 1]
    return classA, classB


# ===== 使用示例 =====
if __name__ == "__main__":
    # 1. 先加载模型（只调用一次）
    load_yolo("YOLO.onnx", use_gpu=False)

    # 2. 多次推理（全局变量 SESSION 复用）
    for img_path in ["aaa.jpg", "bbb.jpg"]:
        img = cv2.imread(img_path)[:, :, ::-1]  # BGR -> RGB
        classA, classB = run_yolo(img)
        print("\n类别A:")
        if classA:
            for i, d in enumerate(classA, 1):
                print(f"  {i}. x={d['x']:.1f}, y={d['y']:.1f}, w={d['w']:.1f}, h={d['h']:.1f}, conf={d['conf']:.2f}")
        else:
            print("  无检测到目标")

        print("\n类别B:")
        if classB:
            for i, d in enumerate(classB, 1):
                print(f"  {i}. x={d['x']:.1f}, y={d['y']:.1f}, w={d['w']:.1f}, h={d['h']:.1f}, conf={d['conf']:.2f}")
        else:
            print("  无检测到目标")

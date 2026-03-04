import cv2
import os
from ml_load import load_yolo
from ml_yolo import run_yolo
from tqdm import tqdm

from variables import true_dir, yolo_file


def save_yolo_labels(img_path, classA, classB):


    img = cv2.imread(img_path)
    h, w = img.shape[:2]

    save_dir = os.path.dirname(img_path)
    base = os.path.splitext(os.path.basename(img_path))[0]
    label_path = os.path.join(save_dir, base + ".txt")

    lines = []
    for d in classA:
        # 中心点和宽高归一化
        cx = d['x'] / w
        cy = d['y'] / h
        bw = d['w'] / w
        bh = d['h'] / h
        lines.append(f"0 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")
    for d in classB:
        cx = d['x'] / w
        cy = d['y'] / h
        bw = d['w'] / w
        bh = d['h'] / h
        lines.append(f"1 {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}")

    with open(label_path, "w") as f:
        f.write("\n".join(lines))

    print(f"保存完成: {label_path}")



def label():


    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)

    # 遍历 true_dir 里的所有图片
    files = os.listdir(true_dir)
    for file in tqdm(files, desc="处理图片", unit="张"):
        img_path = os.path.join(true_dir, file)
        if not file.lower().endswith(".jpg"):
            continue  # 跳过非图片文件
        img = cv2.imread(img_path)  # 这里转成对象
        if img is None:
            raise ValueError("图片读取失败")
        classA, classB = run_yolo(img, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS)
        save_yolo_labels(img_path, classA, classB)

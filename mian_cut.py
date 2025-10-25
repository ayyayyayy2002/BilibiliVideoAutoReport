import cv2
import os
from ml_load import load_yolo, load_siamese
from ml_siamese import run_siamese
from ml_yolo import run_yolo
from tqdm import tqdm
from utils_capcha import crop_detections
from variables import true_dir, yolo_file, siamese_file, save_dir


def cut():


    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)
    SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS = load_siamese(siamese_file)
    files = os.listdir(true_dir)
    for file in tqdm(files, desc="处理图片", unit="张"):
        img_path = os.path.join(true_dir, file)
        if not file.lower().endswith(".jpg"):
            continue  # 跳过非图片文件
        img = cv2.imread(img_path)
        if img is None:
            raise ValueError("图片读取失败")

        # 检测目标
        classA, classB = run_yolo(img, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS)
        cropped_A, cropped_B = crop_detections(img, classA, classB)

        # 相似度匹配
        results_2d = run_siamese(cropped_A, cropped_B, SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS)

        # 为每个 classA 保存对应匹配
        for idx_a, row in enumerate(results_2d, start=1):
            max_idx = row.index(max(row))  # 匹配到的 classB 索引
            folder_name = f"{os.path.splitext(file)[0]}_{idx_a}"
            folder_path = os.path.join(save_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)

            # 保存 A 和匹配到的 B
            # 保存 A 和匹配到的 B
            cv2.imwrite(os.path.join(folder_path, "1.jpg"), cv2.cvtColor(cropped_A[idx_a - 1], cv2.COLOR_BGR2GRAY))
            cv2.imwrite(os.path.join(folder_path, "2.jpg"), cv2.cvtColor(cropped_B[max_idx], cv2.COLOR_BGR2GRAY))




#coding=utf-8
import os
from src import ver_onnx
from src import yolo_onnx
from src import utils


class JYClick(object):
    def __init__(self, per_path='pre_model_v6.onnx', yolo_path='yolo.onnx'):
        save_path = os.path.join(os.path.dirname(__file__))
        path = lambda a, b: os.path.join(a, b)
        per_path = path(save_path, per_path)
        yolo_path = path(save_path, yolo_path)
        self.yolo = yolo_onnx.YOLOV5_ONNX(yolo_path, classes=['char', 'target'],providers=['CPUExecutionProvider'])
        self.pre = ver_onnx.PreONNX(per_path, providers=['CPUExecutionProvider'])

    def run(self, image_path):
        img = utils.open_image(image_path)
        data = self.yolo.decect(image_path)

        # 提取 targets 和 chars 的边界框坐标
        targets = [i.get("crop") for i in data if i.get("classes") == "target"]
        chars = [i.get("crop") for i in data if i.get("classes") == "char"]

        # 根据信息排序
        chars.sort(key=lambda x: x[0])  # 按照 x 坐标排序

        # 获取原始图片的宽高
        img_width, img_height = img.size

        # 将每个目标转换为 YOLO 格式
        yolo_labels = []

        # 处理 targets 类别
        for target in targets:
            class_id = 1  # 将 'target' 的类索引设置为 1
            # 确保 target 是坐标格式 [x1, y1, x2, y2]
            x_center = (target[0] + target[2]) / 2 / img_width
            y_center = (target[1] + target[3]) / 2 / img_height
            width = (target[2] - target[0]) / img_width
            height = (target[3] - target[1]) / img_height

            yolo_labels.append(f"{class_id} {x_center} {y_center} {width} {height}")

        # 处理 chars 类别
        for char in chars:
            class_id = 0  # 将 'char' 的类索引设置为 0
            # 确保 char 是坐标格式 [x1, y1, x2, y2]
            x_center = (char[0] + char[2]) / 2 / img_width
            y_center = (char[1] + char[3]) / 2 / img_height
            width = (char[2] - char[0]) / img_width
            height = (char[3] - char[1]) / img_height

            yolo_labels.append(f"{class_id} {x_center} {y_center} {width} {height}")

        return yolo_labels


def process_all_images_in_directory(directory):
    cap = JYClick()  # 实例化 JYClick 类

    # 获取目录中的所有 .jpg 文件
    jpg_files = [f for f in os.listdir(directory) if f.endswith('.jpg')]

    for jpg_file in jpg_files:
        image_path = os.path.join(directory, jpg_file)
        print(f"Processing {image_path}...")

        result = cap.run(image_path)

        # 保存到与图像相同路径的 .txt 标签文件
        label_file_path = image_path.replace('.jpg', '.txt')
        with open(label_file_path, 'w') as f:
            for label in result:
                f.write(label + '\n')

        print(f"Labels saved to {label_file_path}")


if __name__ == '__main__':
    images_directory = os.path.join(os.path.dirname(__file__),"../","附加文件","失败验证码")  # 替换为您的图像目录路径
    process_all_images_in_directory(images_directory)

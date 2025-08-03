import os
from src import yolo_onnx
from src import ver_onnx
from src import utils

class JYClick(object):
    def __init__(self, per_path='pre_model_v6_quantized.onnx', yolo_path='YOLO.onnx'):
        save_path = os.path.join(os.path.dirname(__file__))
        path = lambda a, b: os.path.join(a, b)
        per_path = path(save_path, per_path)
        yolo_path = path(save_path, yolo_path)
        self.yolo = yolo_onnx.YOLOV5_ONNX(yolo_path, classes=['char', 'target'], providers=['CPUExecutionProvider'])
        self.pre = ver_onnx.PreONNX(per_path, providers=['CPUExecutionProvider'])

    def rotate_image(self, img, angle):
        return img.rotate(angle, expand=True)

    def run(self, image_path):
        img = utils.open_image(image_path)
        data = self.yolo.decect(image_path)
        # 需要选择的字
        targets = [i.get("crop") for i in data if i.get("classes") == "target"]
        chars = [i.get("crop") for i in data if i.get("classes") == "char"]
        # 根据坐标进行排序
        chars.sort(key=lambda x: x[0])
        chars = [img.crop(char) for char in chars]
        result = []

        for m, img_char in enumerate(chars):
            if len(targets) == 0:
                break
            elif len(targets) == 1:
                slys_index = 0
            else:
                img_target_list = []
                for n, target in enumerate(targets):
                    img_target = img.crop(target)
                    img_target_list.append(img_target)
                slys = self.pre.reason_all(img_char, img_target_list)
                slys_index = slys.index(max(slys))
            result.append(targets[slys_index])
            targets.pop(slys_index)
            if len(targets) == 0:
                break

        # 裁剪并保存char和target图片到对应的文件夹
        for i, (char_crop, target_crop) in enumerate(zip(chars, result)):
            # 创建子文件夹
            parent_folder = os.path.dirname(image_path)
            img_name = os.path.splitext(os.path.basename(image_path))[0]
            sub_folder = os.path.join(parent_folder, f"{img_name}_{i + 1}")
            os.makedirs(sub_folder, exist_ok=True)

            # 保存原始及旋转的char和target图片
            for j, angle in enumerate([0, 90, 180, 270]):
                char_img = self.rotate_image(char_crop.resize((105, 105)), angle)
                target_img = self.rotate_image(img.crop(target_crop).resize((105, 105)), angle)

                char_img.save(os.path.join(sub_folder, f"char_{i + 1}_{j}.png"))
                target_img.save(os.path.join(sub_folder, f"target_{i + 1}_{j}.png"))


if __name__ == '__main__':
    folder_path = "../附加文件/失败验证码"
    jpg_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

    cap = JYClick()
    for jpg_file in jpg_files:
        image_path = os.path.join(folder_path, jpg_file)
        cap.run(image_path)

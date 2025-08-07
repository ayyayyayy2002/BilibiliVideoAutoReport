from src import yolo_onnx
from src import ver_onnx
from src import utils
import os

class JYClick(object):
    def __init__(self, per_path='pre_model_v6_quantized.onnx', yolo_path='YOLO.onnx'):
        save_path = os.path.join(os.path.dirname(__file__))
        path = lambda a, b: os.path.join(a, b)
        per_path = path(save_path, per_path)
        yolo_path = path(save_path, yolo_path)
        self.yolo = yolo_onnx.YOLOV5_ONNX(yolo_path, classes=['char', 'target'], providers=['CPUExecutionProvider'])
        self.pre = ver_onnx.PreONNX(per_path, providers=['CPUExecutionProvider'])

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
        return result


if __name__ == '__main__':
    cap = JYClick()
    os.chdir(os.path.join(os.path.dirname(__file__),"../","附加文件","失败验证码"))
    for file_name in os.listdir("."):
        if file_name.endswith(".jpg"):
            image_path = file_name
            result = cap.run(image_path)
            new_file_name = f"...{file_name}"
            utils.drow_img(image_path, result, new_file_name)





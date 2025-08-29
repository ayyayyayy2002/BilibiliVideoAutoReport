import cv2
import numpy as np
from ml_load import load_siamese

# ===== 工具函数 =====
def preprocess(img, target_size=(105, 105)):
    import cv2
    import numpy as np

    # 1. 统一缩放到 105×105
    img = cv2.resize(img, target_size, interpolation=cv2.INTER_LANCZOS4)
    # 2. 归一化到 0-1，保持 RGB 三通道
    img = img.astype(np.float32) / 255.0
    # 3. HWC → CHW（3, 105, 105）
    img = img.transpose(2, 0, 1)

    return img

def run_siamese(a_imgs, b_imgs,SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS):
    """输入多张 A 图像对象、多张 B 图像对象，输出二维数组：
       每个 A 对应一个列表，列表里是该 A 与所有 B 的相似度
    """


    # 对输入图片进行预处理
    a_imgs = [preprocess(img) for img in a_imgs]
    b_imgs = [preprocess(img) for img in b_imgs]

    # 构造所有组合
    pairs = [(ai, bi) for ai in a_imgs for bi in b_imgs]
    a_data = np.stack([p[0] for p in pairs], axis=0)
    b_data = np.stack([p[1] for p in pairs], axis=0)

    # 模型推理
    results = SIAMESE_MODEL.run(
        [SIAMESE_OUTPUTS],
        {SIAMESE_INPUTS[0]: a_data, SIAMESE_INPUTS[1]: b_data}
    )[0]
    results = results.squeeze(axis=1)  # shape (N,)

    # 整理成二维列表
    output = []
    num_b = len(b_imgs)
    for i in range(len(a_imgs)):
        output.append(results[i * num_b:(i + 1) * num_b].tolist())

    return output





# ===== 测试入口 =====
if __name__ == "__main__":
    load_siamese("siamese.onnx", use_gpu=False)

    # 这里外部读取图片（改成你需要的方式，比如 cv2.imread 或 PIL.Image）
    A1 = cv2.cvtColor(cv2.imread("A1.jpg"), cv2.COLOR_BGR2RGB)
    A2 = cv2.cvtColor(cv2.imread("A2.jpg"), cv2.COLOR_BGR2RGB)
    B1 = cv2.cvtColor(cv2.imread("B1.jpg"), cv2.COLOR_BGR2RGB)
    B2 = cv2.cvtColor(cv2.imread("B2.jpg"), cv2.COLOR_BGR2RGB)

    a_imgs = [A1, A2]
    b_imgs = [B1, B2]

    results_2d = run_siamese(a_imgs, b_imgs)

    for i, row in enumerate(results_2d):
        print(f"A{i + 1} vs all B:", row)



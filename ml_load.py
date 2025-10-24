import onnxruntime as ort




def load_yolo(model_path, use_gpu=False):


    providers = ["CUDAExecutionProvider"] if use_gpu else ["CPUExecutionProvider"]
    YOLO_MODEL = ort.InferenceSession(model_path, providers=providers)
    YOLO_INPUTS = YOLO_MODEL.get_inputs()[0].name
    YOLO_OUTPUTS = YOLO_MODEL.get_outputs()[0].name
    return YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS
def load_siamese(model_path, use_gpu=False):
    """加载 Siamese ONNX 模型"""

    providers = ["CUDAExecutionProvider"] if use_gpu else ["CPUExecutionProvider"]
    SIAMESE_MODEL = ort.InferenceSession(model_path, providers=providers)
    SIAMESE_INPUTS = [inp.name for inp in SIAMESE_MODEL.get_inputs()]
    SIAMESE_OUTPUTS = SIAMESE_MODEL.get_outputs()[0].name
    return SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS

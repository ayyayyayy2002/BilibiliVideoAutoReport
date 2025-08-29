import time
import cv2
import numpy
from urllib.parse import urlparse, unquote
import os
import re
import requests
from ml_load import load_yolo, load_siamese
from ml_siamese import run_siamese
from ml_yolo import run_yolo
from selenium.webdriver import ActionChains
from utils_capcha import crop_detections
from utils_chrome import start_chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions


def benchmark():
    base_dir = os.getcwd()
    yolo_file = os.path.join(base_dir, 'model', 'yolo.onnx')
    siamese_file = os.path.join(base_dir, 'model', 'siamese.onnx')
    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)
    SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS = load_siamese(siamese_file)
    user_data_dir = os.path.join(base_dir, 'chrome-win', 'Benchmarker')
    driver = start_chrome(user_data_dir, True, None)
    while True:
        try:

            driver.get("https://space.bilibili.com")

            input1 = WebDriverWait(driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input')
                )
            )
            input1.clear()
            input1.send_keys("11111")

            input2 = WebDriverWait(driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[3]/input')
                )
            )
            input2.clear()
            input2.send_keys("22222")
            submit = WebDriverWait(driver, 5).until(
                expected_conditions.visibility_of_element_located(
                    (By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[2]/div[2]')
                )
            )
            submit.click()
            while True:
                img = WebDriverWait(driver, 5).until(
                    expected_conditions.presence_of_element_located(
                        (By.XPATH, '//*[@class="geetest_item_wrap"]'))
                )
                f = img.get_attribute('style')
                attempt = 0  # 初始化尝试计数
                while ('url("' not in f) and (attempt < 10):
                    f = img.get_attribute('style')
                    attempt += 1
                    time.sleep(0.5)
                print(attempt)
                url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)
                content = requests.get(url, timeout=(5, 10),proxies=None).content

                # 将 bytes 转为 NumPy 数组
                nparr = numpy.frombuffer(content, numpy.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # shape=(H,W,3)

                # 转为 RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # 传入 run_yolo
                classA, classB = run_yolo(img, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS)
                print("\n类别A:")
                if classA:
                    for i, d in enumerate(classA, 1):
                        print(
                            f"  {i}. x={d['x']:.1f}, y={d['y']:.1f}, w={d['w']:.1f}, h={d['h']:.1f}, conf={d['conf']:.2f}")
                else:
                    print("  无检测到目标")

                print("\n类别B:")
                if classB:
                    for i, d in enumerate(classB, 1):
                        print(
                            f"  {i}. x={d['x']:.1f}, y={d['y']:.1f}, w={d['w']:.1f}, h={d['h']:.1f}, conf={d['conf']:.2f}")
                else:
                    print("  无检测到目标")
                cropped_A, cropped_B = crop_detections(img, classA, classB)
                results_2d = run_siamese(cropped_A, cropped_B, SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS)
                selected = []
                for row in results_2d:
                    max_idx = row.index(max(row))  # 找到每行最大值的索引
                    selected.append(classB[max_idx])
                img_elem = driver.find_element(By.CLASS_NAME, 'geetest_big_item')

                # 元素宽度（正方形，宽=高）
                elem_size = img_elem.size['width']

                # 原始模型图像大小
                orig_size = 344

                # 遍历 YOLO 输出目标
                for d in selected:
                    # YOLO 框中心坐标
                    x_model = d['x']
                    y_model = d['y']

                    # 以元素中心为基准计算偏移
                    x_offset = (x_model / orig_size) * elem_size - elem_size / 2
                    y_offset = (y_model / orig_size) * elem_size - elem_size / 2

                    print(f"点击偏移量: ({x_offset:.1f}, {y_offset:.1f})")

                    # 点击
                    ActionChains(driver).move_to_element_with_offset(img_elem, x_offset, y_offset).click().perform()
                    time.sleep(0.5)

                # 执行点击确认按钮的操作
                element = WebDriverWait(driver, 10).until(
                    expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip'))
                )
                element.click()  # 提交验证码
                try:

                    WebDriverWait(driver, 3).until(
                        expected_conditions.invisibility_of_element_located(
                            (By.XPATH, '//*[@class="geetest_item_wrap"]')))
                    print("验证码已消失！")  # 等待 'geetest_item_wrap' 元素消失，表示验证码提交成功
                    fname = os.path.basename(urlparse(unquote(url)).path)  # 去掉 query，取原始文件名
                    file_path = os.path.join(base_dir,'captcha','true' ,fname)
                    with open(file_path, 'wb') as fp:
                        fp.write(content)
                    break
                except Exception as e:
                    print('验证码未消失')
                    fname = os.path.basename(urlparse(unquote(url)).path)  # 去掉 query，取原始文件名
                    file_path = os.path.join(base_dir,'captcha','true' ,fname)
                    with open(file_path, 'wb') as fp:
                        fp.write(content)













        except Exception as e:
            print(e)

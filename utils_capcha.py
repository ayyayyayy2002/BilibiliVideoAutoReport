import pickle
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from urllib.parse import urlparse, unquote
from ml_siamese import run_siamese
from ml_yolo import run_yolo
import requests
import numpy
import time
import cv2
import re
import os
from utils_accuracy import calc_accuracy
from variables import reporter_cookie_file, base_dir


def crop_detections(img, classA, classB):
    cropped_A = []
    for d in classA:
        x, y, w, h = int(d["x"] - d["w"] / 2), int(d["y"] - d["h"] / 2), int(d["w"]), int(d["h"])
        x, y = max(0, x), max(0, y)
        cropped_A.append(img[y:y + h, x:x + w])

    # 按x坐标排序
    cropped_A = [img for _, img in sorted(zip([d["x"] for d in classA], cropped_A), key=lambda x: x[0])]

    cropped_B = []
    for d in classB:
        x, y, w, h = int(d["x"] - d["w"] / 2), int(d["y"] - d["h"] / 2), int(d["w"]), int(d["h"])
        x, y = max(0, x), max(0, y)
        cropped_B.append(img[y:y + h, x:x + w])

    return cropped_A, cropped_B


def capcha(aid,driver, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS,
           SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS):

    while True:

        try:
            url = f"https://www.bilibili.com/appeal/?avid={aid}"
            driver.get(url)


            WebDriverWait(driver, 20, 1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]'))
            ).click()

            WebDriverWait(driver, 20, 1).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div/div[2]/div[2]/div[2]/div[1]/div[2]/label/div[2]/textarea'))
            ).send_keys('视频封面标题以及内容违规')

            while True:
                # 点击确认
                WebDriverWait(driver, 20, 1).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div/div[3]/div[2]'))
                ).click()

                try:
                    WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]'))
                    )
                    break  # 如果元素出现则退出循环
                except Exception as e:
                    print(f"验证码元素未出现{e}")
                    return

            while True:
                img = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located(
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
                proxies = {
                    "http": None,
                    "https": None
                }
                content = requests.get(url, timeout=(3, 3),proxies=proxies).content
                #print(url)

                # 将 bytes 转为 NumPy 数组
                nparr = numpy.frombuffer(content, numpy.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # shape=(H,W,3)

                # 转为 RGB
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # 传入 run_yolo
                classA, classB = run_yolo(img,YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS)

                cropped_A, cropped_B = crop_detections(img, classA, classB)
                results_2d = run_siamese(cropped_A, cropped_B,SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS)

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
                    EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip'))
                )
                element.click()  # 提交验证码
                try:

                    WebDriverWait(driver, 3).until(
                        EC.invisibility_of_element_located((By.XPATH, '//*[@class="geetest_item_wrap"]')))
                    print("验证码已消失！")  # 等待 'geetest_item_wrap' 元素消失，表示验证码提交成功
                    fname = os.path.basename(urlparse(unquote(url)).path)  # 去掉 query，取原始文件名
                    file_path = os.path.join(base_dir, 'captcha', 'true', fname)
                    with open(file_path, 'wb') as fp:
                        fp.write(content)
                    time.sleep(2)
                    calc_accuracy()


                    break
                except Exception as e:
                    print(f'验证码未消失{e}')
                    fname = os.path.basename(urlparse(unquote(url)).path)  # 去掉 query，取原始文件名
                    file_path = os.path.join(base_dir, 'captcha', 'false', fname)
                    with open(file_path, 'wb') as fp:
                        fp.write(content)


            break
        except Exception as e:
            raise RuntimeError(f"人机验证出错: {e}")
    cookies = driver.get_cookies()
    pickle.dump(cookies, open(reporter_cookie_file, "wb"))
    return

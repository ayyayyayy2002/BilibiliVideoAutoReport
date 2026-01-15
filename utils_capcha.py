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
from utils_proxy import switch_proxy
from variables import reporter_cookie_file, false_dir, true_dir


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


def capcha(aid, page, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS,
           SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS):
    while True:
        try:
            url = f"https://www.bilibili.com/appeal/?avid={aid}"
            page.goto(url, wait_until="domcontentloaded")

            # 点击违规申诉按钮
            page.locator('xpath=/html/body/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]').click()

            # 填写违规说明
            page.locator('xpath=/html/body/div/div[2]/div[2]/div[2]/div[1]/div[2]/label/div[2]/textarea') \
                .fill('视频封面标题以及内容违规')

            while True:
                page.locator('xpath=/html/body/div/div[3]/div[2]').click()
                try:
                    page.wait_for_selector('.geetest_item_wrap', timeout=3000)
                    break
                except:
                    print("验证码元素未出现")
                    switch_proxy()

            while True:
                img_elem = page.wait_for_selector('.geetest_item_wrap', timeout=5000)
                f = img_elem.get_attribute('style')
                attempt = 0
                while 'url("' not in f and attempt < 10:
                    f = img_elem.get_attribute('style')
                    attempt += 1
                    time.sleep(0.5)
                print(attempt)

                url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)
                proxies = None
                content = requests.get(url, timeout=(3, 3), proxies=proxies).content

                nparr = numpy.frombuffer(content, numpy.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                classA, classB = run_yolo(img, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS)
                cropped_A, cropped_B = crop_detections(img, classA, classB)
                results_2d = run_siamese(cropped_A, cropped_B, SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS)

                selected = []
                for row in results_2d:
                    max_idx = row.index(max(row))
                    selected.append(classB[max_idx])

                # Playwright 点击
                img_box = img_elem.bounding_box()
                elem_size = img_box['width']
                orig_size = 344

                for d in selected:
                    x_model = d['x']
                    y_model = d['y']
                    x_offset = (x_model / orig_size) * elem_size - elem_size / 2
                    y_offset = (y_model / orig_size) * elem_size - elem_size / 2
                    print(f"点击偏移量: ({x_offset:.1f}, {y_offset:.1f})")
                    page.mouse.click(img_box['x'] + elem_size / 2 + x_offset,
                                     img_box['y'] + elem_size / 2 + y_offset)
                    time.sleep(0.5)
                try:
                    page.locator('.geetest_commit_tip').click(timeout=1000)
                    page.wait_for_selector('.geetest_item_wrap', state='hidden', timeout=3000)
                    print("验证码正确")
                    fname = os.path.basename(urlparse(unquote(url)).path)
                    true_path = os.path.join(true_dir, fname)
                    with open(true_path, 'wb') as fp:
                        fp.write(content)
                    time.sleep(2)
                    calc_accuracy()
                    break
                except Exception as e:
                    print('验证码错误')
                    print(e)
                    fname = os.path.basename(urlparse(unquote(url)).path)
                    false_path = os.path.join(false_dir, fname)
                    with open(false_path, 'wb') as fp:
                        fp.write(content)
                    page.locator('xpath=/html/body/div[2]/div[2]/div[6]/div/div/div[3]/div/a[2]').click()
                    print("刷新验证码")
            break
        except Exception as e:
            raise RuntimeError(f"人机验证出错: {e}")

    # 保存 cookies 到 storage_state 文件
    context = page.context
    context.storage_state(path=reporter_cookie_file)
    return

from urllib.parse import urlparse, unquote
import variables
from ml_siamese import run_siamese
from ml_yolo import run_yolo
import requests
import numpy
import time
import cv2
import re
import os
from utils_accuracy import calc_accuracy
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


def capcha(page,i):
    while True:
        wrap = page.wait_for_selector('.geetest_item_wrap', timeout=variables.timeout.browser)
        page.wait_for_function(
            """el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                return bg && bg.includes('url');
            }""",
            arg=wrap,
            timeout=variables.timeout.browser
        )
        style = wrap.evaluate(
            "el => window.getComputedStyle(el).backgroundImage"
        )
        url = re.search(r'url\(["\']?(.*?)["\']?\)', style).group(1)
        content = requests.get(url, timeout=variables.timeout.request, proxies=None).content

        nparr = numpy.frombuffer(content, numpy.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        classA, classB = run_yolo(img)
        cropped_A, cropped_B = crop_detections(img, classA, classB)
        results_2d = run_siamese(cropped_A, cropped_B)

        selected = []
        available_B = classB.copy()  # 剩余可选 B
        results_matrix = [row.copy() for row in results_2d]  # 剩余相似度矩阵

        for row_idx, row in enumerate(results_matrix):
            if not available_B:
                break  # 没有可选 B 时退出
            # 找出当前 row 中最大值的索引（在 available_B 中）
            max_idx = row.index(max(row))
            selected.append(available_B[max_idx])
            # 删除已选 B
            del available_B[max_idx]
            # 删除 results_matrix 中对应列
            for r in results_matrix:
                del r[max_idx]

        # Playwright 点击
        img_box = wrap.bounding_box()
        elem_size = img_box['width']
        orig_size = 344

        for d in selected:
            x_model = d['x']
            y_model = d['y']
            x_offset = (x_model / orig_size) * elem_size - elem_size / 2
            y_offset = (y_model / orig_size) * elem_size - elem_size / 2
            print(f"点击偏移量: ({x_offset:.1f}, {y_offset:.1f})")
            page.mouse.click(img_box['x'] + elem_size / 2 + x_offset,img_box['y'] + elem_size / 2 + y_offset)
            time.sleep(0.5)
        page.locator('div.geetest_commit_tip', has_text="确认").click(timeout=variables.timeout.browser)#提交验证码
        try:
            page.wait_for_selector('.geetest_item_wrap', state='hidden', timeout=3000)
            print("验证码正确")
            time.sleep(2)
            if variables.log:
                fname = os.path.basename(urlparse(unquote(url)).path)
                true_path = os.path.join(variables.path.true_path, fname)
                with open(true_path, 'wb') as fp:
                    fp.write(content)
                calc_accuracy()
            break
        except Exception as e:
            print('验证码错误',e)
            if variables.log:
                fname = os.path.basename(urlparse(unquote(url)).path)
                false_path = os.path.join(variables.path.false_path, fname)
                with open(false_path, 'wb') as fp:
                    fp.write(content)
                calc_accuracy()
    return

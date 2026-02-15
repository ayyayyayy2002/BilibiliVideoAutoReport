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
from variables import reporter_cookie_file, false_dir, true_dir, timeout_request, timeout_browser


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


def capcha(aid, page, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS, SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS):
    while True:
         try:
            url = f"https://www.bilibili.com/appeal/?avid={aid}"
            page.goto(url, wait_until="domcontentloaded")
            page.locator('xpath=/html/body/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]').click(timeout=timeout_browser)
            page.locator('xpath=/html/body/div/div[2]/div[2]/div[2]/div[1]/div[2]/label/div[2]/textarea').fill('视频封面标题以及内容违规')
            page.locator('xpath=/html/body/div/div[3]/div[2]').click(timeout=timeout_browser)
            page.wait_for_selector('.geetest_item_wrap', timeout=timeout_browser)
            break
         except Exception as e:
             print("验证码元素未出现",e)
             context = page.context
             context.storage_state(path=reporter_cookie_file)
             return


    while True:
        wrap = page.wait_for_selector('.geetest_item_wrap', timeout=timeout_browser)
        page.wait_for_function(
            """el => {
                const bg = window.getComputedStyle(el).backgroundImage;
                return bg && bg.includes('url');
            }""",
            arg=wrap,
            timeout=timeout_browser
        )
        style = wrap.evaluate(
            "el => window.getComputedStyle(el).backgroundImage"
        )
        url = re.search(r'url\(["\']?(.*?)["\']?\)', style).group(1)
        content = requests.get(url, timeout=timeout_request, proxies=None).content

        nparr = numpy.frombuffer(content, numpy.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        classA, classB = run_yolo(img, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS)
        cropped_A, cropped_B = crop_detections(img, classA, classB)
        results_2d = run_siamese(cropped_A, cropped_B, SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS)

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
            page.mouse.click(img_box['x'] + elem_size / 2 + x_offset,
                             img_box['y'] + elem_size / 2 + y_offset)
            time.sleep(0.5)
        page.locator('xpath=/html/body/div[2]/div[2]/div[6]/div/div/div[3]/a').click(timeout=timeout_browser)#提交验证码
        try:
            page.wait_for_selector('.geetest_item_wrap', state='hidden', timeout=timeout_browser)
            print("验证码正确")
            fname = os.path.basename(urlparse(unquote(url)).path)
            true_path = os.path.join(true_dir, fname)
            with open(true_path, 'wb') as fp:
                fp.write(content)
            time.sleep(2)
            calc_accuracy()
            break
        except Exception as e:
            print('验证码错误',e)
            fname = os.path.basename(urlparse(unquote(url)).path)
            false_path = os.path.join(false_dir, fname)
            with open(false_path, 'wb') as fp:
                fp.write(content)




    context = page.context
    context.storage_state(path=reporter_cookie_file)
    return

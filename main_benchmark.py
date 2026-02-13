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
from utils_accuracy import calc_accuracy
from utils_capcha import crop_detections
from utils_chrome import start_chrome
from variables import yolo_file, siamese_file, false_dir, true_dir, timeout_browser, timeout_request


def benchmark():
    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)
    SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS = load_siamese(siamese_file)

    # Playwright 启动干净浏览器
    playwright, browser, context, page = start_chrome(headless=False, proxy_url=None)

    while True:
        try:
            page.goto("https://space.bilibili.com", wait_until="domcontentloaded")

            # 转 Selenium 的 WebDriverWait 逻辑为 Playwright selector
            input1 = page.wait_for_selector('//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input',
                                            timeout=timeout_browser)
            input1.fill("11111")

            input2 = page.wait_for_selector('//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[3]/input',
                                            timeout=timeout_browser)
            input2.fill("22222")

            submit = page.wait_for_selector('//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[2]/div[2]', timeout=timeout_browser)
            submit.click()

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
                page.locator('xpath=/html/body/div[3]/div[2]/div[6]/div/div/div[3]/a/div').click(
                    timeout=timeout_browser)  # 提交验证码
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
                    print('验证码错误', e)
                    fname = os.path.basename(urlparse(unquote(url)).path)
                    false_path = os.path.join(false_dir, fname)
                    with open(false_path, 'wb') as fp:
                        fp.write(content)



        except Exception as e:
            print(e)

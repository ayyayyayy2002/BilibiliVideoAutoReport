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
from variables import yolo_file, siamese_file, false_dir, true_dir, timeout_browser


def benchmark():
    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)
    SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS = load_siamese(siamese_file)

    # Playwright 启动干净浏览器
    playwright, browser, context, page = start_chrome(headless=True, proxy_url=None)

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
                img_elem = page.wait_for_selector('//*[@class="geetest_item_wrap"]', timeout=timeout_browser)
                f = img_elem.get_attribute('style')
                attempt = 0
                while ('url("' not in f) and (attempt < 10):
                    f = img_elem.get_attribute('style')
                    attempt += 1
                    time.sleep(0.5)
                print(attempt)
                url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)
                content = requests.get(url, timeout=timeout, proxies=None).content

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
                for i, row in enumerate(results_2d):
                    print(f"A{i + 1} vs all B:", row)

                selected = []
                for row in results_2d:
                    max_idx = row.index(max(row))
                    selected.append(classB[max_idx])

                img_elem = page.query_selector('.geetest_big_item')
                elem_size = img_elem.bounding_box()['width']
                orig_size = 344

                for d in selected:
                    x_model = d['x']
                    y_model = d['y']
                    x_offset = (x_model / orig_size) * elem_size - elem_size / 2
                    y_offset = (y_model / orig_size) * elem_size - elem_size / 2
                    print(f"点击偏移量: ({x_offset:.1f}, {y_offset:.1f})")
                    page.mouse.click(img_elem.bounding_box()['x'] + elem_size / 2 + x_offset,
                                     img_elem.bounding_box()['y'] + elem_size / 2 + y_offset)
                    time.sleep(0.5)

                element = page.wait_for_selector('.geetest_commit_tip', timeout=10000)
                element.click()

                try:
                    page.wait_for_selector('.geetest_item_wrap', state='detached', timeout=3000)
                    print("验证码已消失！")
                    fname = os.path.basename(urlparse(unquote(url)).path)
                    true_path = os.path.join(true_dir, fname)
                    with open(true_path, 'wb') as fp:
                        fp.write(content)
                    calc_accuracy()
                    break
                except:
                    print('验证码未消失')
                    fname = os.path.basename(urlparse(unquote(url)).path)
                    false_path = os.path.join(false_dir, fname)
                    with open(false_path, 'wb') as fp:
                        fp.write(content)

        except Exception as e:
            print(e)

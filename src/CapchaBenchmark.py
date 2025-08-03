from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium import webdriver
import JYClick
import requests
import time
import os
import re




base_dir = os.path.dirname(os.path.abspath(__file__))
chrome_binary_path = os.path.join(base_dir, '附加文件', 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, '附加文件', 'chromedriver.exe')
success_directory = os.path.join(base_dir, '运行记录', '成功验证码')
fail_directory = os.path.join(base_dir, '运行记录', '失败验证码')





def get_location(target):
    # 获取元素在屏幕上的位置信息
    location = target.location
    size = target.size
    height = size['height']
    width = size['width']
    left = location['x']
    top = location['y']
    right = left + width
    bottom = top + height
    script = f"return {{'left': {left}, 'top': {top}, 'right': {right}, 'bottom': {bottom}}};"
    rect = driver.execute_script(script)
    left_x = int(rect['left'])
    top_y = int(rect['top'])
    return left_x, top_y



username = "13485629454"
password ="***********"

proxies = {'http': None, 'https': None}
options = webdriver.ChromeOptions()
options.binary_location = chrome_binary_path  # 指定 Chrome 浏览器的可执行文件路径
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
#options.add_argument("--headless")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  #禁用缓存
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
driver.set_window_position(0, 0)  # 设置浏览器窗口位置（x, y）

url = f"https://space.bilibili.com/"
driver.get(url)


input_element = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input'))
)
input_element.send_keys(username)

input_element = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[3]/input'))
)
input_element.send_keys(password)

while True:

    url = f"https://space.bilibili.com/"
    driver.get(url)

    input_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input'))
    )
    input_element.send_keys(username)

    input_element = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[3]/input'))
    )
    input_element.send_keys(password)
    #time.sleep(999993)

    while True:
        # 点击确认
        WebDriverWait(driver, 20, 1).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[2]/div[2]'))
        ).click()

        # 检查元素是否存在
        try:
            img = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@class="geetest_item_wrap"]'))
            )
            print("验证码元素已出现！")
            break  # 如果元素出现则退出循环
        except Exception:
            print("验证码元素未出现，重新点击确认...")

    while True:
        f = img.get_attribute('style')
        attempt = 0  # 初始化尝试计数
        while ('url("' not in f) and (attempt < 10):
            f = img.get_attribute('style')
            attempt += 1
            time.sleep(0.5)
        url = re.search(r'url\("([^"]+?)\?[^"]*"\);', f).group(1)
        print(url)
        content = requests.get(url, proxies=proxies, timeout=(5, 10)).content
        plan = JYClick.JYClick().run(content)
        print(plan)
        a, b = get_location(img)
        lan_x = 306 / 334
        lan_y = 343 / 384

        for crop in plan:
            x1, y1, x2, y2 = crop
            x, y = [(x1 + x2) / 2, (y1 + y2) / 2]
            print(a + x * lan_x, b + y * lan_y, "点击坐标")

            # 执行点击操作
            ActionChains(driver).move_by_offset(a + x * lan_x, b + y * lan_y).click().perform()
            ActionChains(driver).move_by_offset(-(a + x * lan_x),
                                                -(b + y * lan_y)).perform()  # 恢复鼠标位置
            time.sleep(0.3)

        try:  # 执行点击确认按钮的操作
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, 'geetest_commit_tip'))
            )
            element.click()  # 提交验证码

            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element_located(
                    (By.XPATH, '//*[@class="geetest_item_wrap"]'))
            )
            print("验证码已消失！")
            os.makedirs(success_directory, exist_ok=True)
            success_name = url.split('/')[-1]
            success_path = os.path.join(success_directory, success_name)
            with open(success_path, 'wb') as file:
                file.write(content)




        except Exception as e:
            print(f"提交验证码时发生错误: {e}")
            os.makedirs(fail_directory, exist_ok=True)
            fail_name = url.split('/')[-1]
            fail_path = os.path.join(fail_directory, fail_name)
            with open(fail_path, 'wb') as file:
                file.write(content)
            print('已点击刷新按钮')



        break


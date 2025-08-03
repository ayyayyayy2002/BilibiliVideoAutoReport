from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from dotenv import load_dotenv, set_key
from selenium import webdriver
import qrcode
import time
import re
import os


########################################################################################################################
proxies = {'http': None, 'https': None}
base_dir = os.path.dirname(os.path.abspath(__file__))
chrome_binary_path = os.path.join(base_dir, 'chrome-win', 'chrome.exe')
chrome_driver_path = os.path.join(base_dir, 'chrome-win', 'chromedriver.exe')
env_file = os.path.join(base_dir, '.env')
load_dotenv(dotenv_path=env_file)










user_data_dir = os.path.join(base_dir, 'User Data','Reporter')
options = webdriver.ChromeOptions()
options.binary_location = chrome_binary_path
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  # 禁用缓存
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
driver.get("https://space.bilibili.com")
print(f'\n举报账号登陆中\n')
try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="app-main"]/div/div[2]/div[1]/div[2]/div[1]/div'))
    )
    title = element.get_attribute('title')
    qr = qrcode.QRCode()
    qr.add_data(title)
    qr.make()
    qr.print_ascii(out=None, tty=False, invert=False)

except Exception as e:
    print('无法获取二维码元素')


while True:
    current_url = driver.current_url
    match = re.search(r'/(\d+)$', current_url)
    if match:
        uid = match.group(1)
        print(f"已登录: {uid}")
        break
    time.sleep(2)

cookies = driver.get_cookies()
COOKIE = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
UA = driver.execute_script("return navigator.userAgent;")
driver.quit()




set_key(env_file, 'UA', UA)
set_key(env_file, 'reportor', COOKIE)





user_data_dir = os.path.join(base_dir, 'User Data','Collector')
options = webdriver.ChromeOptions()
options.binary_location = chrome_binary_path
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(f'--user-data-dir={user_data_dir}')
options.add_argument('--proxy-server="direct://"')
options.add_argument('--proxy-bypass-list=*')
options.add_argument("--disable-gpu")
options.add_argument("--disable-sync")
options.add_argument("disable-cache")  # 禁用缓存
options.add_argument('log-level=3')
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)  # 启动 Chrome 浏览器
driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）
driver.get("https://space.bilibili.com")
print(f'\n主号登陆中\n')
try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located(
            (By.XPATH, '//*[@id="app-main"]/div/div[2]/div[1]/div[2]/div[1]/div'))
    )
    title = element.get_attribute('title')
    qr = qrcode.QRCode()
    qr.add_data(title)
    qr.make()
    qr.print_ascii(out=None, tty=False, invert=False)

except Exception as e:
    print('无法获取二维码元素')


while True:
    current_url = driver.current_url
    match = re.search(r'/(\d+)$', current_url)
    if match:
        uid = match.group(1)
        print(f"已登录: {uid}")
        break
    time.sleep(2)

cookies = driver.get_cookies()
COOKIE = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
driver.quit()
set_key(env_file, 'collector', COOKIE)




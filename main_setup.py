from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from dotenv import load_dotenv, set_key
import time
import re
import os
from utils_chrome import start_chrome

########################################################################################################################
def setup():
    base_dir = os.getcwd()
    user_data_dir = os.path.join(base_dir, 'chrome-win','Reporter')
    env_file = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path=env_file)
    proxy = os.getenv('PROXY')
    driver=start_chrome(user_data_dir,False,proxy)
    driver.get("https://space.bilibili.com")

    try:
        element = WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, '//*[@id="app-main"]/div/div[2]/div[1]/div[2]/div[1]/div'))
        )
    except Exception as e:
        print('无法获取二维码元素')
    while True:
        current_url = driver.current_url
        match = re.search(r'/(\d+)$', current_url)
        if match:
            uid = match.group(1)
            print(f"已登录: {uid}")
            break
        time.sleep(1)

    cookies = driver.get_cookies()
    COOKIE = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    UA = driver.execute_script("return navigator.userAgent;")
    driver.quit()
    set_key(env_file, 'UA', UA)
    set_key(env_file, 'reporter', COOKIE)
    user_data_dir = os.path.join(base_dir, 'chrome-win','Collector')
    driver=start_chrome(user_data_dir,False,proxy)
    driver.get("https://space.bilibili.com")

    try:
        element = WebDriverWait(driver, 5).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, '//*[@id="app-main"]/div/div[2]/div[1]/div[2]/div[1]/div'))
        )
    except Exception as e:
        print('无法获取二维码元素')
    while True:
        current_url = driver.current_url
        match = re.search(r'/(\d+)$', current_url)
        if match:
            uid = match.group(1)
            print(f"已登录: {uid}")
            break
        time.sleep(1)

    cookies = driver.get_cookies()
    COOKIE = '; '.join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    driver.quit()
    set_key(env_file, 'collector', COOKIE)




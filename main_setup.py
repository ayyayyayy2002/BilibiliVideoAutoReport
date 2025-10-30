import re
import time
import pickle
from utils_chrome import start_chrome
from variables import reporter_cookie_file, base_dir, collector_cookie_file


def setup():
    print("登录Reporter")
    driver = start_chrome( headless=False,proxy_url="")
    driver.get("https://space.bilibili.com")
    while True:
        match = re.search(r'/(\d+)$', driver.current_url)
        if match:
            uid = match.group(1)
            print(f"已登录: {uid}")
            break
        time.sleep(1)

    cookies = driver.get_cookies()
    pickle.dump(cookies, open(reporter_cookie_file, "wb"))
    driver.quit()

    print("登录Collector")
    driver = start_chrome( headless=False,proxy_url="")
    driver.get("https://space.bilibili.com")
    while True:
        match = re.search(r'/(\d+)$', driver.current_url)
        if match:
            uid = match.group(1)
            print(f"已登录: {uid}")
            break
        time.sleep(1)

    cookies = driver.get_cookies()
    pickle.dump(cookies, open(collector_cookie_file, "wb"))
    driver.quit()


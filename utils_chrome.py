import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

from variables import chrome_binary_path, chrome_driver_path


def start_chrome(headless: bool = False, proxy_url: str = None):

    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-sync")
    options.add_argument("disable-cache")
    options.add_argument('log-level=3')


    # 代理
    if proxy_url:
        options.add_argument(f'--proxy-server={proxy_url}')
    else:
        options.add_argument('--proxy-server="direct://"')
        options.add_argument('--proxy-bypass-list=*')

    # 无头
    if headless:
        options.add_argument("--headless=new")

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1000, 700)
    return driver


# 示例调用
if __name__ == "__main__":
    # 使用用户目录 "chrome-win/Reporter"，不开启无头，不用代理
    driver = start_chrome( headless=False, proxy_url=None)
    driver.get("https://www.baidu.com")

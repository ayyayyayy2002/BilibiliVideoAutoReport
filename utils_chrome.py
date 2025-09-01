import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def start_chrome(user_data_dir: str, headless: bool = False, proxy_url: str = None):
    base_dir = os.getcwd()
    chrome_binary_path = os.path.join(base_dir, 'chrome-win', 'chrome.exe')
    chrome_driver_path = os.path.join(base_dir, 'chrome-win', 'chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.binary_location = chrome_binary_path
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-sync")
    options.add_argument("disable-cache")  # 禁用缓存
    options.add_argument('log-level=3')

    # 设置代理
    if proxy_url:
        options.add_argument(f'--proxy-server={proxy_url}')
    else:
        options.add_argument('--proxy-server="direct://"')
        options.add_argument('--proxy-bypass-list=*')

    # 是否无头
    if headless:
        options.add_argument("--headless=new")  # 新版 headless 模式更稳定

    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1000, 700)

    return driver


# 示例调用
if __name__ == "__main__":
    # 使用用户目录 "chrome-win/Reporter"，不开启无头，不用代理
    driver = start_chrome(user_data_dir="chrome-win/Reporter", headless=False, proxy_url=None)
    driver.get("https://www.baidu.com")

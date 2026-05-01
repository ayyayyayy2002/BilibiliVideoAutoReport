import time
from playwright.sync_api import sync_playwright

import variables


def start_browser(headless=False, proxy_url=None):
    playwright = sync_playwright().start()

    launch_options = {
        "executable_path": variables.path.chrome_file,
        "headless": headless,
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-sync",
            "--disable-cache",
            "--log-level=3",
        ],
    }

    if proxy_url:
        launch_options["args"].append(f"--proxy-server={proxy_url}")
    else:
        launch_options["args"].extend([
            "--proxy-server=direct://",
            "--proxy-bypass-list=*"
        ])

    browser = playwright.chromium.launch(**launch_options)
    return playwright, browser


if __name__ == "__main__":
    # 启动浏览器
    playwright, browser = start_browser(proxy_url="127.0.0.1:7890")

    # 创建上下文
    context_options = {
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "storage_state": "model/reporter0.json"  # 可选
    }
    context = browser.new_context(**context_options)

    # 创建页面
    page = context.new_page()
    page.set_viewport_size({"width": 1000, "height": 700})
    page.goto("https://www.baidu.com")

    # 验证UA
    current_ua = page.evaluate("navigator.userAgent")
    print(f"当前浏览器UA: {current_ua}")

    time.sleep(500)
    context.close()
    browser.close()
    playwright.stop()
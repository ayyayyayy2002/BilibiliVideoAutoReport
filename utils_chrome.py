import time
from playwright.sync_api import sync_playwright

from variables import chrome_binary_path


def start_chrome(headless=False, proxy_url=None, storage_state=None, user_agent=None):
    playwright = sync_playwright().start()

    launch_options = {
        "executable_path": chrome_binary_path,
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

    # 启动浏览器
    browser = playwright.chromium.launch(**launch_options)

    # 创建上下文时的配置项
    context_options = {}
    if storage_state and storage_state.strip():
        context_options["storage_state"] = storage_state
    # 如果传入了user_agent，则添加到上下文配置中
    if user_agent:
        context_options["user_agent"] = user_agent

    # 根据配置创建上下文
    context = browser.new_context(**context_options)

    page = context.new_page()
    page.set_viewport_size({"width": 1000, "height": 700})

    return playwright, browser, context, page


if __name__ == "__main__":
    # 自定义UA示例（可以替换成任意你需要的UA）
    custom_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

    playwright, browser, context, page = start_chrome(
        proxy_url="127.0.0.1:7890",
        user_agent=custom_ua  # 传入自定义UA
    )
    page.goto("https://www.baidu.com")
    # 验证UA是否生效（可选）
    current_ua = page.evaluate("navigator.userAgent")
    print(f"当前浏览器UA: {current_ua}")

    time.sleep(500)
    context.close()
    browser.close()
    playwright.stop()
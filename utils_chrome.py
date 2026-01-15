import time
from playwright.sync_api import sync_playwright


def start_chrome(headless=False, proxy_url=None, storage_state=None):
    playwright = sync_playwright().start()

    launch_options = {
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

    # 根据是否传 storage_state 决定 context
    if storage_state and storage_state.strip():
        context = browser.new_context(storage_state=storage_state)
    else:
        context = browser.new_context()

    page = context.new_page()
    page.set_viewport_size({"width": 1000, "height": 700})

    return playwright, browser, context, page


if __name__ == "__main__":
    playwright, browser, context, page = start_chrome(
        proxy_url="127.0.0.1:7890",
    )
    page.goto("https://www.baidu.com")
    time.sleep(500)
    context.close()
    browser.close()
    playwright.stop()

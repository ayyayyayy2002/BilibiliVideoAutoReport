import os
from tqdm import tqdm

import variables
from utils_chrome import start_browser


def checkuid():
    uids = []

    try:
        with open(variables.path.black_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.isdigit():
                    uids.append(line)
    except Exception as e:
        print(f"无法读取UID文件: {e}")
        return "0"

    if not uids:
        print("uid.txt 文件中没有可处理的UID，程序退出")
        return "0"

    # 使用 Playwright 启动浏览器
    storage_state = os.path.join('model', f'reporter0.json') if os.path.exists(os.path.join('model', f'reporter0.json')) else None
    playwright, browser = start_browser(headless=False, proxy_url=variables.clash.url_proxy)
    context_options = {
        "user_agent": variables.UA,
        "storage_state": storage_state
    }
    context = browser.new_context(**context_options)
    page = context.new_page()
    page.set_viewport_size({"width": 1000, "height": 700})

    try:
        for uid in tqdm(uids):
            url = f'https://space.bilibili.com/{uid}/dynamic'
            print(f"打开UID：https://space.bilibili.com/{uid}/dynamic")
            page.goto(url)

            print("请按回车继续...")
            input()  # 等待用户操作


    finally:
        # 关闭 Playwright 浏览器
        context.close()
        browser.close()
        playwright.stop()

    return 0

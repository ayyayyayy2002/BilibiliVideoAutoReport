import os
from utils_chrome import start_chrome
from variables import reporter_cookie_file, collector_cookie_file

def setup():
    # ------------------- Reporter 登录 -------------------
    print("登录Reporter")
    # 如果文件存在就传入 storage_state，否则为 None
    storage_state = reporter_cookie_file if os.path.exists(reporter_cookie_file) else None
    playwright, browser, context, page = start_chrome(headless=False, storage_state=storage_state)
    page.goto("https://space.bilibili.com")

    page.wait_for_selector(".nickname", timeout=300000)
    nickname = page.query_selector(".nickname").inner_text()
    print("已登录，昵称:", nickname)

    # 保存最新状态
    context.storage_state(path=reporter_cookie_file)

    context.close()
    browser.close()
    playwright.stop()

    # ------------------- Collector 登录 -------------------
    print("登录Collector")
    storage_state = collector_cookie_file if os.path.exists(collector_cookie_file) else None
    playwright, browser, context, page = start_chrome(headless=False, storage_state=storage_state)
    page.goto("https://space.bilibili.com")

    if storage_state:
        print("Collector 导入 cookie 成功")
    else:
        print("Collector 没有 cookie 文件，需要手动登录")
    # 等待昵称元素出现，说明已经登录
    page.wait_for_selector(".nickname", timeout=300000)
    nickname = page.query_selector(".nickname").inner_text()
    print("已登录，昵称:", nickname)

    context.storage_state(path=collector_cookie_file)

    context.close()
    browser.close()
    playwright.stop()

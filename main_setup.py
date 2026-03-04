import os

from utils_chrome import start_browser
#from utils_chrome import start_chrome
from variables import collector_cookie_file, CLASH_PROXY_URL, accountcount, UA


def setup():
    # ------------------- Collector 登录 -------------------
    print("登录Collector")
    storage_state = collector_cookie_file if os.path.exists(collector_cookie_file) else None
    playwright, browser = start_browser(headless=False,proxy_url=CLASH_PROXY_URL)
    context_options = {
        "user_agent": UA,
        "storage_state": storage_state
    }
    context = browser.new_context(**context_options)
    page = context.new_page()
    page.set_viewport_size({"width": 1000, "height": 700})
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
    # ------------------- Reporter 登录 -------------------
    for i in range(0, accountcount):
        print(f"登录Reporter{i+1}")
        # 如果文件存在就传入 storage_state，否则为 None
        storage_state = os.path.join('model', f'reporter{i}.json')  if os.path.exists(os.path.join('model', f'reporter{i}.json') ) else None
        playwright, browser= start_browser(headless=False,proxy_url=CLASH_PROXY_URL)
        context_options = {
            "user_agent": UA,
            "storage_state": storage_state
        }
        context = browser.new_context(**context_options)
        page = context.new_page()
        page.set_viewport_size({"width": 1000, "height": 700})
        page.goto("https://space.bilibili.com")

        page.wait_for_selector(".nickname", timeout=300000)
        nickname = page.query_selector(".nickname").inner_text()
        print(f"Reporter{i}已登录，昵称:", nickname)

        # 保存最新状态
        context.storage_state(path=os.path.join('model', f'reporter{i}.json') )

        context.close()
        browser.close()
        playwright.stop()



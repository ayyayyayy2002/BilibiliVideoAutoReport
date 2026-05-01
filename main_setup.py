import os
from utils_chrome import start_browser
import variables


def setup():
    for i in range(0, variables.accountcount):
        print(f"登录账号{i}")
        storage_state =  os.path.join(variables.path.cookie_path, f'{i}.json')
        playwright, browser= start_browser(headless=False)
        context_options = {
            "user_agent": variables.UA,
            "storage_state":storage_state if os.path.exists(storage_state) else None
        }
        context = browser.new_context(**context_options)
        page = context.new_page()
        page.set_viewport_size({"width": 1000, "height": 700})
        page.goto("https://space.bilibili.com")
        page.wait_for_selector(".nickname", timeout=300000)
        nickname = page.query_selector(".nickname").inner_text()
        print(f"Reporter{i}已登录，昵称:", nickname)
        context.storage_state(path=storage_state)
        context.close()
        browser.close()
        playwright.stop()



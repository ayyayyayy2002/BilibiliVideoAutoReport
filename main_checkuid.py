import os

from utils_chrome import start_chrome
from variables import uid_file, reporter_cookie_file, timeout_browser


def checkuid():
    uids = []

    try:
        with open(uid_file, 'r', encoding='utf-8') as file:
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
    storage_state = reporter_cookie_file if os.path.exists(reporter_cookie_file) else None
    playwright, browser, context, page = start_chrome(headless=False, storage_state=storage_state)

    try:
        for uid in uids:
            url = f'https://space.bilibili.com/{uid}/dynamic'
            print(f"打开UID：{uid}")
            page.goto(url)

            print("请按回车继续...")
            input()  # 等待用户操作

            # 删除已经处理的 UID
            try:
                with open(uid_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                with open(uid_file, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != uid:
                            f.write(line)
                print(f"删除UID: {uid}")
            except Exception as e:
                print(f"删除UID时发生错误: {e}")
    finally:
        # 关闭 Playwright 浏览器
        context.close()
        browser.close()
        playwright.stop()

    return "0"

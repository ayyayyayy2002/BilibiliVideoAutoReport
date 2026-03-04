import os
from main_benchmark import benchmark
from main_checkuid import checkuid
from main_getuid import getuid
from main_label import label
from main_report import report
from main_setup import setup
from mian_LOOP import LOOP
from mian_cut import cut
from utils_chrome import start_browser
from variables import CLASH_PROXY_URL, UA, accountcount


def main():

    os.environ["TEMP"] = "record"
    print("请输入数字选择要运行的函数：")
    print("1. 开始举报 LOOP()")
    print("2. 设置账号 setup()")
    print("3. 获取UID getuid()")
    print("4. 举报UID report()")
    print("5. 查看UID checkuid()")
    print("6. 模型测试 benchmark()")
    print("7. 图片标记 label()")
    print("8. 图片裁切 cut()")

    choice = input("请输入：")



    if choice == "2":
        setup()
    elif choice == "3":
        getuid()
    elif choice == "4":
        pages = []
        playwright, browser = start_browser(headless=False, proxy_url=CLASH_PROXY_URL)
        context_options = {
            "user_agent":UA,
            "storage_state":os.path.join('model', f'reporter0.json')
        }
        context = browser.new_context(**context_options)
        page = context.new_page()
        page.set_viewport_size({"width": 1000, "height": 700})
        pages.append(page)
        report(pages)
    elif choice == "5":
        checkuid()
    elif choice == "6":
         benchmark()
    elif choice == "7":
        label()
    elif choice == "8":
        cut()
    else:
        pages = []
        playwright, browser = start_browser(headless=True, proxy_url=CLASH_PROXY_URL)
        for i in range(0, accountcount):
            context_options = {
                "user_agent": UA,
                "storage_state": os.path.join('model', f'reporter{i}.json')
            }
            context = browser.new_context(**context_options)
            page = context.new_page()
            page.set_viewport_size({"width": 1000, "height": 700})
            pages.append(page)
        LOOP(pages)
    main()


if __name__ == "__main__":
    main()

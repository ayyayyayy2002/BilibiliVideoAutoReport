import os
from main_benchmark import benchmark
from main_checkuid import checkuid
from main_getuid import getuid
from main_label import label
from main_report import report
from main_setup import setup
from mian_cut import cut
from ml_load import load_yolo, load_siamese
from utils_chrome import start_browser
from utils_proxy import switch_proxy
import variables


def main():
    print("请输入数字选择要运行的函数：")
    print("1. 开始举报")
    print("2. 设置账号 setup()")
    print("3. 获取UID getuid()")
    print("4. 举报UID report()")
    print("5. 查看UID checkuid()")
    print("6. 模型测试 benchmark()")
    print("7. 图片标记 label()")
    print("8. 图片裁切 cut()")
    choice = input("请输入：")



    if choice == "2":
        print("2. 设置账号 setup()")
        setup()
    elif choice == "3":
        print("3. 获取UID getuid()")
        getuid()
    elif choice == "4":
        print("4. 举报UID report()")
        variables.Global.YOLO_MODEL, variables.Global.YOLO_INPUTS, variables.Global.YOLO_OUTPUTS = load_yolo(variables.path.yolo_file)
        variables.Global.SIAMESE_MODEL, variables.Global.SIAMESE_INPUTS, variables.Global.SIAMESE_OUTPUTS = load_siamese(variables.path.siamese_file)
        pages = [""]
        playwright, browser = start_browser(headless=True, proxy_url=variables.clash.url_proxy)
        for i in range(1, variables.accountcount):
            context_options = {
                "user_agent": variables.UA,
                "storage_state": os.path.join(variables.path.cookie_path, f'{i}.json')
            }
            context = browser.new_context(**context_options)
            page = context.new_page()
            page.set_viewport_size({"width": 1000, "height": 700})
            pages.append(page)
        report(pages)
    elif choice == "5":
        print("5. 查看UID checkuid()")
        checkuid()
    elif choice == "6":
         print("6. 模型测试 benchmark()")
         benchmark()
    elif choice == "7":
        print("7. 图片标记 label()")
        label()
    elif choice == "8":
        print("8. 图片裁切 cut()")
        cut()
    else:
        print("1. 开始举报")
        variables.Global.YOLO_MODEL, variables.Global.YOLO_INPUTS, variables.Global.YOLO_OUTPUTS = load_yolo(variables.path.yolo_file)
        variables.Global.SIAMESE_MODEL, variables.Global.SIAMESE_INPUTS, variables.Global.SIAMESE_OUTPUTS = load_siamese(variables.path.siamese_file)
        pages = [""]
        playwright, browser = start_browser(headless=True, proxy_url=variables.clash.url_proxy)
        for i in range(1,variables.accountcount ):
            context_options = {
                "user_agent":variables.UA,
                "storage_state": os.path.join(variables.path.cookie_path, f'{i}.json')
            }
            context = browser.new_context(**context_options)
            page = context.new_page()
            page.set_viewport_size({"width": 1000, "height": 700})
            pages.append(page)

        count = 0

        skip = True
        while True:
            while True:
                if skip:
                    skip = False
                    break
                try:

                    result = getuid()
                    if result == "0":
                        if count >= variables.cycle != 0:
                            print("已达到最大循环次数,终止")
                            return
                        break
                except Exception as e:
                    print(e)
                    switch_proxy()
            while True:
                try:
                    result = report(pages)
                    print(result)
                    if result == "0":
                        count += 1
                        break
                except Exception as e:
                    print(e)
                    switch_proxy()

    main()


if __name__ == "__main__":
    proxies=None
    current_proxy=None
    os.environ["TEMP"] = "file"
    main()

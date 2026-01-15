import os

from main_benchmark import benchmark
from main_checkuid import checkuid
from main_getuid import getuid
from main_label import label
from main_report import report
from main_setup import setup
from mian_LOOP import LOOP
from mian_cut import cut
from utils_chrome import start_chrome
from variables import reporter_cookie_file


def main():
    os.makedirs("temp", exist_ok=True)
    os.environ["TEMP"] = "temp"
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
        _, _,_, page = start_chrome(headless=True, proxy_url="127.0.0.1:7890", storage_state=reporter_cookie_file)
        report(page)
    elif choice == "5":
        checkuid()
    elif choice == "6":
        benchmark()
    elif choice == "7":
        label()
    elif choice == "8":
        cut()
    else:
        _, _,_, page = start_chrome(headless=True, proxy_url="127.0.0.1:7890", storage_state=reporter_cookie_file)
        LOOP(page)


if __name__ == "__main__":
    main()

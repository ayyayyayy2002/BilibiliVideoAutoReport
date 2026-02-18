import os

from main_benchmark import benchmark
from main_checkuid import checkuid
from main_getuid import getuid
from main_label import label
from main_report import report
from main_setup import setup
from main_uidsql import uidsql
from mian_LOOP import LOOP
from mian_cut import cut
from utils_chrome import start_chrome
from variables import reporter_cookie_file, CLASH_PROXY_URL, UA


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
    print("9. 用户信息 uidsql()")

    choice = input("请输入：")



    if choice == "2":
        setup()
    elif choice == "3":
        getuid()
    elif choice == "4":
        _, _,_, page = start_chrome(headless=False, proxy_url=CLASH_PROXY_URL, storage_state=reporter_cookie_file,user_agent=UA)
        report(page)
    elif choice == "5":
        checkuid()
    elif choice == "6":
        benchmark()
    elif choice == "7":
        label()
    elif choice == "8":
        cut()
    elif choice == "9":
        uidsql()
    else:
        _, _,_, page = start_chrome(headless=True, proxy_url=CLASH_PROXY_URL, storage_state=reporter_cookie_file,user_agent=UA)
        LOOP(page)
    main()


if __name__ == "__main__":
    main()

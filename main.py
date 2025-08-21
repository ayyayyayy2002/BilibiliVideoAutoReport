from main_check import check
from main_getuid import getuid
from main_report import report
from main_setup import setup
from mian_LOOP import LOOP


def main():
    print("请输入数字选择要运行的函数：")
    print("1. LOOP()")
    print("2. setup()")
    print("3. getuid()")
    print("4. report()")
    print("5. check()")

    choice = input("请输入：")


    if choice == "1":
        LOOP()
    elif choice == "2":
        setup()
    elif choice == "3":
        getuid()
    elif choice == "4":
        report()
    elif choice == "5":
        check()
    else:
        print("输入无效")


if __name__ == "__main__":
    main()

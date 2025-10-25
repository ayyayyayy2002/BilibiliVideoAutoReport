from main_benchmark import benchmark
from main_checkuid import checkuid
from main_getuid import getuid
from main_label import label
from main_report import report
from main_setup import setup
from mian_LOOP import LOOP
from mian_cut import cut


def main():

    print("请输入数字选择要运行的函数：")
    print("1. LOOP()")
    print("2. setup()")
    print("3. getuid()")
    print("4. report()")
    print("5. checkuid()")
    print("6. benchmark()")
    print("7. label()")
    print("8. cut()")

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
        checkuid()
    elif choice == "6":
        benchmark()
    elif choice == "7":
        label()
    elif choice == "8":
        cut()
    else:
        LOOP()


if __name__ == "__main__":
    main()

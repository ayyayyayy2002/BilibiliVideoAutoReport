from main_getuid import getuid
from main_report import report
from utils_proxy import switch_proxy
from variables import cycle


def LOOP(page):
    count=0


    skip=True
    while True:
        while True:
            if skip:
                skip=False
                break
            try:

                result = getuid()
                if result =="0":
                    if count >= cycle:
                        print("已达到最大循环次数,终止")
                        return
                    break
            except Exception as e:
                print(e)
                switch_proxy()
        while True:
            try:
                result = report(page)
                print(result)
                if result == "0" :
                    count+=1
                    break
            except Exception as e:
                print(e)
                switch_proxy()

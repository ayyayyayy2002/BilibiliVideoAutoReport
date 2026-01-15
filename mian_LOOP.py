from main_getuid import getuid
from main_report import report
from utils_proxy import switch_proxy


def LOOP(page):


    skip=True
    while True:
        while True:
            if skip:
                skip=False
                break
            try:

                result = getuid()
                if result =="0":
                    break
            except Exception as e:
                print(e)
        while True:
            try:
                result = report(page)
                print(result)
                if result == "0" :
                    break
            except Exception as e:
                print(e)
                switch_proxy()

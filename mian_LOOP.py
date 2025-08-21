from main_getuid import getuid
from main_report import report


def LOOP():

    skip=True
    while True:
        while True:
            if skip:
                skip=False
                break
            try:

                result = getuid()
                print(result)
                if result =="0":

                    break
            except Exception as e:
                print(e)
        while True:
            try:
                result = report()
                print(result)
                if result == "0" :
                    break
            except Exception as e:
                print(e)
import os
from dotenv import load_dotenv
from main_getuid import getuid
from main_report import report
from utils_proxy import switch_proxy


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
                base_dir = os.getcwd()
                env_file = os.path.join(base_dir, '.env')
                load_dotenv(dotenv_path=env_file)
                group = os.getenv('group')
                switch_proxy(group)
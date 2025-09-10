from ml_load import load_yolo, load_siamese
from dotenv import load_dotenv, set_key
from utils_chrome import start_chrome
from utils_proxy import switch_proxy
from utils_capcha import capcha
from datetime import datetime
from utils_avtobv import enc
import requests
import random
import re
import os



def report():
    base_dir = os.getcwd()
    uid_file = os.path.join(base_dir, 'list', 'uid')
    uids={}

    try:
        with open(uid_file, 'r', encoding='utf-8') as file:  # 以读取模式打开文件
            for line in file:
                line = line.strip()  # 去掉行首尾的空白字符
                if line.isdigit():
                    uids.add(line)
    except Exception as e:
        print(f"无法读取UID文件: {e}")
        return "0"

    if not uids:
        print("uid.txt 文件中没有可处理的UID，程序退出")
        return "0"

    for uid in uids:

















        











        try:
            with open(uid_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(uid_file, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip() != uid:
                        f.write(line)
            print(f"删除UID: {uid}")
        except Exception as e:
            return f"删除UID时发生错误: {e}"



        print(f'\nhttps://space.bilibili.com/{uid}\n')
        reportcount = 0


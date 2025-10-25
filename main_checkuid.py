import os
from selenium import webdriver
from utils_chrome import start_chrome
from variables import uid_file


def checkuid():


    uids =  []

    try:
        with open(uid_file, 'r', encoding='utf-8') as file:  # 以读取模式打开文件
            for line in file:
                line = line.strip()  # 去掉行首尾的空白字符
                if line.isdigit():
                    uids.append(line)
    except Exception as e:
        print(f"无法读取UID文件: {e}")
        return "0"

    if not uids:
        print("uid.txt 文件中没有可处理的UID，程序退出")
        return "0"
    driver = webdriver.Chrome()
    driver.set_window_size(1200, 800)
    for uid in uids:
        print(f"打开UID：{uid}")
        driver.get(f'https://space.bilibili.com/{uid}/videos')
        print("请按回车继续...")
        input()  # 程序会在这里暂停，直到用户按回车

        try:
            with open(uid_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            with open(uid_file, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip() != uid:
                        f.write(line)
            print(f"删除UID: {uid}")
        except Exception as e:
            print(f"删除UID时发生错误: {e}")
    return "0"


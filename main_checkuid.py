import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def checkuid():
    base_dir = os.getcwd()
    uid_file = os.path.join(base_dir, 'list', 'uid')
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

    for uid in uids:
        username = os.getlogin()  # 获取当前登录系统的用户名
        chrome_options = Options()
        chrome_options.add_argument(f"--user-data-dir=C:/Users/{username}/AppData/Local/Google/Chrome/User Data")
        chrome_options.add_argument("--profile-directory=Default")
        driver = webdriver.Chrome( options=chrome_options)
        driver.get(f'https://space.bilibili.com/{uid}')

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


from selenium import webdriver
import os


def check():


    uids = []
    base_dir = os.getcwd()
    uid_file = os.path.join(base_dir, "list",'uid')
    user_data_dir = f"C:/Users/{os.environ['USERNAME']}/AppData/Local/Google/Chrome/User Data"
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument('--proxy-server="direct://"')
    options.add_argument('--proxy-bypass-list=*')
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-sync")
    options.add_argument("disable-cache")  # 禁用缓存
    options.add_argument('log-level=3')
    driver = webdriver.Chrome(options=options)  # 启动 Chrome 浏览器
    driver.set_window_size(1000, 700)  # 设置浏览器窗口大小（宽度, 高度）

    try:
        with open(uid_file, 'r', encoding='utf-8') as file:  # 以读取模式打开文件
            for line in file:
                line = line.strip()  # 去掉行首尾的空白字符
                uids.append(line)
    except Exception as e:
        print(f"无法读取UID文件: {e}")
        exit(0)

    for uid in uids:
        driver.get(f"https://space.bilibili.com/{uid}/video")
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
        input("请按回车键继续...")





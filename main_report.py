import pickle

from ml_load import load_yolo, load_siamese
from utils_chrome import start_chrome
from utils_proxy import switch_proxy
from utils_capcha import capcha
from datetime import datetime
from utils_avtobv import enc
import requests
import random
import re
import os

from variables import base_dir, yolo_file, siamese_file, reporter_cookie_file, proxies, UA, group, reason, uid_file, \
    black_file


def report():

    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)
    SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS = load_siamese(siamese_file)
    uids = set()
    cookies = pickle.load(open(reporter_cookie_file, "rb"))
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)



    tids_with_weights = {
        '2': 1,  # 违法违禁
        '5': 1,  # 赌博诈骗
        '10025': 1,  # 违法信息外链
        '10014': 1,  # 涉政谣言
        '10015': 1,  # 涉社会事件谣言
        '10017': 1,  # 虚假不实信息
        '10018': 1,  # 违规推广
        '52': 1,  # 转载/自制错误
        '10019': 1,  # 其他不规范行为
        '7': 1,  # 人身攻击
        '9': 1,  # 引战
        '3': 10,  # 色情低俗
        '10020': 1,  # 危险行为
        '10021': 1,  # 观感不适
        '6': 1,  # 血腥暴力
        '10000': 1,  # 青少年不良信息
        '10022': 1,  # 其他
    }
    tids = list(tids_with_weights.keys())
    weights = list(tids_with_weights.values())

    os.system("taskkill /f /im chromium.exe /t >nul 2>&1")
    os.system("taskkill /f /im chromedriver.exe /t >nul 2>&1")

    driver = start_chrome( True, "")
    driver.get("https://space.bilibili.com")
    for c in cookies:
        c.pop("sameSite", None)
        c.pop("expiry", None)
        try:
            driver.add_cookie(c)
        except:
            pass

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

    session = requests.Session()



    session.headers.update({
        'user-agent': UA,
        'cookie': COOKIE
    })

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
        date = datetime.now().strftime('[%m-%d]')
        aid_log_file = os.path.join(base_dir, 'record', 'report', f'{date}{uid}.txt')
        response = session.get(f'https://api.bilibili.com/x/web-interface/card?mid={uid}', timeout=(5, 10),proxies=proxies)
        data = response.json()
        name = data['data']['card']['name']

        print(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}")
        with open(aid_log_file, 'a', encoding='utf-8') as file:
            file.write(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}3\n")

        aids = []
        titles = []
        pics = []

        response = session.get(f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=0',
                               timeout=(3, 3),proxies=proxies)
        data = response.json()
        for archive in data['data']['archives']:
            aids.append(archive['aid'])
            titles.append(archive['title'])
            pics.append(archive['pic'])
        count = len(aids)
        if name=="账号已注销":
            try:
                with open(black_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                with open(black_file, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != uid:
                            f.write(line)
                print(f"删除UID: {uid}")
            except Exception as e:
                return f"删除UID时发生错误: {e}"
        print(f'普通视频个数:{count}')
        with open(aid_log_file, 'a', encoding='utf-8') as file:
            file.write(f"视频个数:{count}\n")

        print(f'\nhttps://space.bilibili.com/{uid}\n')
        reportcount = 0

        items = list(zip(aids, titles, pics))
        random.shuffle(items)
        for aid, title, pic in zip(aids, titles, pics):
            tid = random.choices(tids, weights=weights, k=1)[0]
            reportcount += 1
            data = {
                'aid': aid,
                'attach': pic,
                'block_author': 'false',
                'csrf': CSRF,
                'desc': reason.replace("title",title),
                'tid': f'{tid}'
            }
            while True:
                try:
                    response = session.post('https://api.bilibili.com/x/web-interface/appeal/v2/submit', data=data,timeout=(3, 3),proxies=proxies)
                    break
                except Exception as e:
                    print(e)
                    switch_proxy(group)

            if "62009" in response.text or reportcount >=15:
                print(f'视频{reportcount:03}:{response.text}，{title}')
                break
            elif "-352" in response.text or "-351" in response.text:
                print(f'视频{reportcount:03}:{response.text}，{title}')
                capcha(aid,driver, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS,
                                SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS)
                cookies = pickle.load(open(reporter_cookie_file, "rb"))
                COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
                session.headers.update({
                    'user-agent': UA,
                    'cookie': COOKIE
                })
            elif "412" in response.text:
                print('报错412，切换代理')
                switch_proxy(group)
            else:
                print(f'视频{reportcount:03}:{response.text}，{title}')

            with open(aid_log_file, 'a', encoding='utf-8') as file:
                file.write(f'{enc(int(aid))},{tid}，{title}\n')



    return "0"

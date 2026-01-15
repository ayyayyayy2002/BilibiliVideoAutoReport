import json
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

from variables import base_dir, yolo_file, siamese_file, reporter_cookie_file, proxies, UA,  reason, uid_file,black_file


def report(page):

    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)
    SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS = load_siamese(siamese_file)
    uids = set()


    with open(reporter_cookie_file, "r", encoding="utf-8") as f:
        storage = json.load(f)

    cookies = storage.get("cookies", [])
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)

    tids_with_weights = {
        '2': 1, '5': 1, '10025': 1, '10014': 1, '10015': 1, '10017': 1, '10018': 1, '52': 1, '10019': 1,
        '7': 1, '9': 1, '3': 10, '10020': 1, '10021': 1, '6': 1, '10000': 1, '10022': 1
    }
    tids = list(tids_with_weights.keys())
    weights = list(tids_with_weights.values())

    page.goto("https://space.bilibili.com")

    for uid in open(uid_file, 'r', encoding='utf-8'):
        uid = uid.strip()
        if uid.isdigit():
            uids.add(uid)

    if not uids:
        print("uid.txt 文件中没有可处理的UID，程序退出")
        return "0"

    session = requests.Session()
    session.headers.update({
        'user-agent': UA,
        'cookie': COOKIE
    })

    for uid in uids:
        # 删除已处理的 UID
        try:
            lines = open(uid_file, 'r', encoding='utf-8').readlines()
            with open(uid_file, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip() != uid:
                        f.write(line)
            print(f"删除UID: {uid}")
        except Exception as e:
            return f"删除UID时发生错误: {e}"

        date = datetime.now().strftime('[%m-%d]')
        aid_log_file = os.path.join(base_dir, 'record',"report" ,f'{date}{uid}.txt')
        response = session.get(f'https://api.bilibili.com/x/web-interface/card?mid={uid}',
                               timeout=(2, 2), proxies=proxies)
        data = response.json()
        name = data['data']['card']['name']

        print(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}")
        with open(aid_log_file, 'a', encoding='utf-8') as file:
            file.write(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}\n")

        aids, titles, pics = [], [], []

        response = session.get(
            f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=0',
            timeout=(3, 3), proxies=proxies
        )
        data = response.json()
        for archive in data['data']['archives']:
            aids.append(archive['aid'])
            titles.append(archive['title'])
            pics.append(archive['pic'])
        count = len(aids)

        if name == "账号已注销":
            try:
                lines = open(black_file, 'r', encoding='utf-8').readlines()
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
        for aid, title, pic in items:
            tid = random.choices(tids, weights=weights, k=1)[0]
            reportcount += 1
            data = {
                'aid': aid,
                'attach': pic,
                'block_author': 'false',
                'csrf': CSRF,
                'desc': reason.replace("title", title),
                'tid': f'{tid}'
            }

            while True:
                try:
                    response = session.post(
                        'https://api.bilibili.com/x/web-interface/appeal/v2/submit',
                        data=data, timeout=(3, 3), proxies=proxies
                    )
                    break
                except Exception as e:
                    print(e)
                    switch_proxy()

            if "62009" in response.text or reportcount >= 50:
                print(f'视频{reportcount:03}:{response.text}，{title}')
                break
            elif "-352" in response.text or "-351" in response.text:
                print(f'视频{reportcount:03}:{response.text}\n{aid}{title}')
                capcha(aid, page, YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS,
                       SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS)
                with open(reporter_cookie_file, "r", encoding="utf-8") as f:
                    storage = json.load(f)

                cookies = storage.get("cookies", [])
                COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
                session.headers.update({
                    'user-agent': UA,
                    'cookie': COOKIE
                })
            elif "412" in response.text:
                print('报错412，切换代理')
                switch_proxy()
            else:
                print(f'视频{reportcount:03}:{response.text}\nhttps://www.bilibili.com/video/av{aid}\n{title}\n')

            with open(aid_log_file, 'a', encoding='utf-8') as file:
                file.write(f'{enc(int(aid))},{tid}，{title}\n')
    return "0"

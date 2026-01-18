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

from variables import yolo_file, siamese_file, reporter_cookie_file, proxies, UA, reason, uid_file, \
    black_file, limit,  report_dir


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
        '10030': 1,#色情低俗
        '10031': 1,#违规广告引流
        '10032': 1,#涉政敏感
        '10033': 1,#引战、网暴、不友善
        '10034': 1,#传播谣言
        '10035': 1,#涉嫌诈骗
        '10036': 1,#引人不适
        '10037': 1,#涉未成年人不良信息
        '10038': 1,#封面党、标题党
        '10039': 1,#其他
    }
    tids = list(tids_with_weights.keys())
    weights = list(tids_with_weights.values())

    page.goto("https://space.bilibili.com")
    try:
        for uid in open(uid_file, 'r', encoding='utf-8'):
            uid = uid.strip()
            if uid.isdigit():
                uids.add(uid)
    except Exception:
        print("读取UID文件出错")
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
        aid_log_file = os.path.join(report_dir ,f'{date}{uid}.txt')
        response = session.get(f'https://api.bilibili.com/x/web-interface/card?mid={uid}',
                               timeout=(2, 2), proxies=None)
        data = response.json()
        name = data['data']['card']['name']

        print(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}")
        with open(aid_log_file, 'a', encoding='utf-8') as file:
            file.write(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}\n")

        aids, titles, pics = [], [], []

        response = session.get(
            f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=0',
            timeout=(3, 3), proxies=None
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
            pic = pic.replace("http:", "")
            data = {
                'aid': aid,
                'attach': pic,
                'block_author': 'false',
                'csrf': CSRF,
                'desc': reason.replace("title", title),
                'meta': '',
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

            if "62009" in response.text or reportcount >= limit:
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

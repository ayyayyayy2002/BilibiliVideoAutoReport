import json
from ml_load import load_yolo, load_siamese
from utils_proxy import switch_proxy
from utils_capcha import capcha
from datetime import datetime
from utils_avtobv import enc
import requests
import random
import re
import os

from variables import yolo_file, siamese_file, reporter_cookie_file, proxies, UA, uid_file, limit, report_dir, \
    tids_with_weights, timeout_request, reasons


def report(page):
    YOLO_MODEL, YOLO_INPUTS, YOLO_OUTPUTS = load_yolo(yolo_file)
    SIAMESE_MODEL, SIAMESE_INPUTS, SIAMESE_OUTPUTS = load_siamese(siamese_file)
    uids = set()

    with open(reporter_cookie_file, "r", encoding="utf-8") as f:
        storage = json.load(f)

    cookies = storage.get("cookies", [])
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)

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
        date = datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')
        aid_log_file = os.path.join(report_dir, f'{date}{uid}.txt')
        print(f"开始举报: https://space.bilibili.com/{uid} TIME: {date}")
        with open(aid_log_file, 'a', encoding='utf-8') as file:
            file.write(f"UID: {uid} TIME: {date}\n")
        aids, titles, pics,durations ,seasons= [], [], [],[],[]
        reportcount = 0

        # ------------------- 合集视频部分 -------------------
        response = session.get(
            f'https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={uid}&page_size=20&page_num=1',
            timeout=timeout_request, proxies=None
        )
        data = response.json()
        for season in data['data']['items_lists']['seasons_list']:
            seasons.append(season['meta']['season_id'])
        for season in seasons:
            response = session.get(
                f'https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid={uid}&season_id={season}&sort_reverse=false&page_size=30&page_num=1',
                timeout=timeout_request, proxies=None
            )
            data = response.json()
            for archive in data['data']['archives']:
                aids.append(archive['aid'])
                titles.append(archive['title'])
                pics.append(archive['pic'])
                durations.append(archive['duration'])

        count = len(aids)
        print(f'合集视频个数:{count}')
        with open(aid_log_file, 'a', encoding='utf-8') as file:
            file.write(f"合集视频个数:{count}\n")

        # ------------------- 投稿视频部分 -------------------
        response = session.get(
            f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=0',
            timeout=timeout_request, proxies=None
        )
        data = response.json()
        for archive in data['data']['archives']:
            aids.append(archive['aid'])
            titles.append(archive['title'])
            pics.append(archive['pic'])
            durations.append(archive['duration'])

        items = list(zip(aids, titles, pics, durations))
        if count==0:
            random.shuffle(items)


        count=len(aids)-count
        print(f'投稿视频个数:{count}')
        with open(aid_log_file, 'a', encoding='utf-8') as file:
            file.write(f"投稿视频个数:{count}\n")

        for aid, title, pic ,duration in items:
            tid = random.choices(tids, weights=weights, k=1)[0]
            reason=random.choice(reasons)
            duration=random.randint(1, duration)
            m = duration // 60
            s = duration % 60
            if m > 0:
                duration=f"{m}分{s}秒"
            else:
                duration=f"{s}秒"
            reason = reason.replace("title", title).replace("duration", duration)
            reportcount += 1
            pic = pic.replace("http:", "")
            data = {
                'aid': aid,
                'attach': pic,
                'block_author': 'false',
                'csrf': CSRF,
                'desc': reason,
                'meta': '',
                'tid': f'{tid}'
            }


            while True:
                try:
                    response = session.post(
                        'https://api.bilibili.com/x/web-interface/appeal/v2/submit',
                        data=data, timeout=timeout_request, proxies=proxies
                    )
                    break
                except Exception as e:
                    print(e)
                    switch_proxy()

            if "62009" in response.text or reportcount >= limit:
                print(f'视频{reportcount:03}:{response.text}，{title}')

                try:
                    lines = open(uid_file, 'r', encoding='utf-8').readlines()
                    with open(uid_file, 'w', encoding='utf-8') as f:
                        for line in lines:
                            if line.strip() != uid:
                                f.write(line)
                    print(f"删除UID: {uid}")
                except Exception as e:
                    return f"删除UID时发生错误: {e}"

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

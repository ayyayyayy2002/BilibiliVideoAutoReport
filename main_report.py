import json
import string
import time

import variables
from ml_load import load_yolo, load_siamese
from utils_proxy import switch_proxy
from utils_capcha import capcha
from datetime import datetime
import requests
import random
import re
import os
from tqdm import tqdm


def report(pages):
    uids = set()
    with open(os.path.join('model', 'reporter0.json'), "r", encoding="utf-8") as f:
        storage = json.load(f)

    cookies = storage.get("cookies", [])
    # 只保留 domain 包含 .bilibili.com 的 cookie
    filtered = [c for c in cookies if ".bilibili.com" in c.get("domain", "")]
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in filtered)

    session = requests.Session()
    session.headers.update({
        'user-agent': UA,
        'cookie': COOKIE
    })

    tids = list(tids_with_weights.keys())
    weights = list(tids_with_weights.values())

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

    for uid in tqdm(uids):
        date = datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')
        print(f"开始举报: https://space.bilibili.com/{uid} TIME: {date}")
        aids, titles, pics, durations, seasons = [], [], [], [], []
        reports = []
        # ------------------- 动态视频部分 -------------------
        response = session.get(
            f'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space?offset=&host_mid={uid}&timezone_offset=-480&platform=web&type=video&features=itemOpusStyle,listOnlyfans,opusBigCover',
            timeout=timeout_request, proxies=proxies)
        data = response.json()
        for item in data['data']['items']:
            major = item.get('modules', {}).get('module_dynamic', {}).get('major', {})
            archive = major.get('archive')
            if not archive:
                continue
            badge_text = archive.get('badge', {}).get('text')
            if badge_text != '动态视频':
                continue
            if archive:
                aids.append(archive.get('aid'))
                titles.append(archive.get('title'))
                pics.append(archive.get('cover'))
                duration_text = archive.get('duration_text', '0:00')
                parts = duration_text.split(':')
                if len(parts) == 2:
                    seconds = int(parts[0]) * 60 + int(parts[1])
                elif len(parts) == 3:
                    seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                else:
                    seconds = int(parts[0])
                durations.append(seconds)

        print(f'动态视频个数:{len(aids)}')
        items = list(zip(aids, titles, pics, durations))
        random.shuffle(items)
        reports.extend(items)

        # ------------------- 合集视频部分 -------------------
        aids, titles, pics, durations, seasons = [], [], [], [], []
        response = session.get(
            f'https://api.bilibili.com/x/polymer/web-space/seasons_series_list?mid={uid}&page_size=20&page_num=1',
            timeout=timeout_request, proxies=proxies)
        data = response.json()
        for season in data['data']['items_lists']['seasons_list']:
            seasons.append(season['meta']['season_id'])
        for season in seasons:
            response = session.get(
                f'https://api.bilibili.com/x/polymer/web-space/seasons_archives_list?mid={uid}&season_id={season}&sort_reverse=false&page_size=30&page_num=1',
                timeout=timeout_request, proxies=proxies)
            data = response.json()
            for archive in data['data']['archives']:
                aids.append(archive['aid'])
                titles.append(archive['title'])
                pics.append(archive['pic'])
                durations.append(archive['duration'])

        print(f'合集视频个数:{len(aids)}')
        items = list(zip(aids, titles, pics, durations))
        random.shuffle(items)
        reports.extend(items)

        # ------------------- 投稿视频部分 -------------------
        aids, titles, pics, durations, seasons = [], [], [], [], []
        response = session.get(f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=0',
                               timeout=timeout_request, proxies=proxies)
        data = response.json()
        for archive in data['data']['archives']:
            aids.append(archive['aid'])
            titles.append(archive['title'])
            pics.append(archive['pic'])
            durations.append(archive['duration'])

        print(f'投稿视频个数:{len(aids)}')
        items = list(zip(aids, titles, pics, durations))
        random.shuffle(items)
        reports.extend(items)
        for i in range(0, accountcount):
            reportcount = 0
            with open(os.path.join('model', f'reporter{i}.json'), "r", encoding="utf-8") as f:
                storage = json.load(f)
            cookies = storage.get("cookies", [])
            filtered = [c for c in cookies if ".bilibili.com" in c.get("domain", "")]
            COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in filtered)
            CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
            session = requests.Session()
            session.headers.update({
                'user-agent': UA,
                'cookie': COOKIE
            })
            # ------------------- 开始举报 -------------------
            for aid, title, pic, duration in reports:
                tid = random.choices(tids, weights=weights, k=1)[0]
                # reason = random.choice(reasons)

                chars = string.ascii_lowercase + string.digits
                length = random.randint(1, 20)
                reason = ''.join(random.choices(chars, k=length))

                duration = random.randint(1, duration)
                m = duration // 60
                s = duration % 60
                if m > 0:
                    duration = f"{m}分{s}秒"
                else:
                    duration = f"{s}秒"
                reason = reason.replace("title", title).replace("duration", duration)
                reportcount += 1
                #pic = pic.replace("http:", "")
                headers = {
                    'accept': '*/*',
                    'accept-language': 'zh-CN,zh;q=0.9',
                    'content-type': 'application/x-www-form-urlencoded',
                    'dnt': '1',
                    'origin': 'https://www.bilibili.com',
                    'priority': 'u=1, i',
                    'referer': 'https://www.bilibili.com/',
                    'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-site',
                }
                data = {
                    'aid': aid,
                    'attach': '',
                    'block_author': 'false',
                    'csrf': CSRF,
                    'desc': reason,
                    'meta': '',
                    'tid': f'{tid}'
                }
                while True:
                    try:
                        response = session.post(
                            'https://api.bilibili.com/x/web-interface/appeal/v2/submit?x-bili-locale-json=%7B%22c_locale%22:%7B%22language%22:%22zh%22,%22region%22:%22CN%22%7D,%22always_translate%22:true%7D', data=data,
                            timeout=variables.timeout.request, proxies=variables.proxy, headers=headers
                        )
                        # print(response.request.headers)
                        break
                    except Exception as e:
                        print(e)
                        switch_proxy()

                if "重复" in response.text  or reportcount >=variables.limit:
                    print(f'账号{i}, 视频{reportcount:03}:{response.text}\nhttps://www.bilibili.com/video/av{aid}\n{title}\n')
                    break
                elif "-352" in response.text:
                    print(f'账号{i}, 视频{reportcount:03}:{response.text}\nhttps://www.bilibili.com/video/av{aid}\n{title}\n')
                    while True:
                        try:
                            url = f"https://www.bilibili.com/appeal/?avid={aid}"
                            pages[i].goto(url, wait_until="domcontentloaded", timeout=variables.timeout.browser)
                            pages[i].locator('xpath=/html/body/div/div[2]/div[2]/div[2]/div[1]/div/div/div[2]').click(timeout=variables.timeout.browser)
                            pages[i].locator('xpath=/html/body/div/div[2]/div[2]/div[2]/div[1]/div[2]/label/div[2]/textarea').fill('视频封面标题以及内容违规')
                            pages[i].locator('xpath=/html/body/div/div[3]/div[2]').click(timeout=variables.timeout.browser)
                            pages[i].wait_for_selector('.geetest_item_wrap', timeout=variables.timeout.browser)
                            break
                        except Exception as e:
                            print("验证码元素未出现", e)
                            switch_proxy()
                    capcha(pages[i], i)
                    context = pages[i].context
                    context.storage_state(path=os.path.join(variables.path.cookie_path, f'{i}.json'))
                    with open(os.path.join(variables.path.cookie_path, f'{i}.json'), "r", encoding="utf-8") as f:
                        storage = json.load(f)
                    cookies = storage.get("cookies", [])
                    filtered = [c for c in cookies if ".bilibili.com" in c.get("domain", "")]
                    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in filtered)
                    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
                    session = requests.Session()
                    session.headers.update({
                        'user-agent': UA,
                        'cookie': COOKIE
                    })
                elif "412" in response.text:
                    print('报错412，切换代理')
                    switch_proxy()
                elif "-351" in response.text:
                    print("疑似cookie失效,请重新登录")
                    exit(1)
                else:
                    print(
                        f'账号{i}, 视频{reportcount:03}:{response.text}\nhttps://www.bilibili.com/video/av{aid}\n{title}\n')

        try:
            lines = open(uid_file, 'r', encoding='utf-8').readlines()
            with open(uid_file, 'w', encoding='utf-8') as f:
                for line in lines:
                    if line.strip() != uid:
                        f.write(line)
            print(f"删除UID: {uid}")
        except Exception as e:
            return f"删除UID时发生错误: {e}"

    return "0"

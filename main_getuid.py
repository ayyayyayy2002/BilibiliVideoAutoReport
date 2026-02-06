import json
import requests
import re
import os

from variables import uid_file, black_file, white_file, keywords_file, UA, reporter_cookie_file, collector_cookie_file, \
    timeout_request


def getuid():

    proxies = None
    lists = set()
    keywords = set()

    if os.path.exists(uid_file):
        print(f"文件 {uid_file} 存在，已删除。")
        os.remove(uid_file)
    else:
        print(f"文件 {uid_file} 不存在，无需删除。")

    # ------------------ Reporter ------------------
    with open(reporter_cookie_file, "r", encoding="utf-8") as f:
        storage = json.load(f)
    cookies = storage.get("cookies", [])
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
    print(f'稍后再看：举报账号')
    headers = {'cookie': COOKIE, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=proxies,
                            timeout=timeout_request)
    print(response)
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        lists.add(str(mid))
        print(mid)

    data_post = {'csrf': CSRF}
    print(CSRF)
    response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data_post,
                             proxies=proxies, timeout=timeout_request)
    print(response.text)

    # ------------------ Collector ------------------
    with open(collector_cookie_file, "r", encoding="utf-8") as f:
        storage = json.load(f)
    cookies = storage.get("cookies", [])
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
    print(f'稍后再看：主号')
    headers = {'cookie': COOKIE, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=proxies,
                            timeout=timeout_request)
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        lists.add(str(mid))
        print(mid)

    data_post = {'csrf': CSRF}
    print(CSRF)
    response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data_post,
                             proxies=proxies, timeout=timeout_request)
    print(response.text)

    # ------------------ 合并黑白名单 ------------------
    for file_path in [black_file, white_file]:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if file_path == black_file:
                    lists.update(lines)
                else:
                    lists.difference_update(lines)

    sorted_lists = sorted(lists, key=int)
    with open(black_file, 'w', encoding='utf-8') as f:
        for uid in sorted_lists:
            f.write(f'{uid}\n')

    # ------------------ 搜索关键词 ------------------
    if os.path.exists(keywords_file):
        with open(keywords_file, 'r', encoding='utf-8') as f:
            for line in f:
                keyword = line.strip()
                if keyword:
                    keywords.add(keyword)

    if keywords:
        for keyword in keywords:
            mids = set()
            headers = {'cookie': COOKIE, 'user-agent': UA}
            print(f"正在搜索关键词：{keyword}")
            response = requests.get(
                f'https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=video',
                headers=headers, proxies=proxies, timeout=timeout_request)
            data = response.json()
            for item in data.get("data", {}).get("result", []):
                mid = item.get("mid")
                if mid is not None:
                    lists.add(str(mid))
                    mids.add(str(mid))
                if len(mids) >= 10:
                    break
            print(f"搜索结果：{mids}")

    sorted_lists = sorted(lists, key=int)
    with open(uid_file, 'w', encoding='utf-8') as f:
        for uid in sorted_lists:
            f.write(f'{uid}\n')

    return "0"

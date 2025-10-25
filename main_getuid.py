import pickle
import requests
import re
import os

from variables import uid_file, black_file, white_file, keywords_file, UA, reporter_cookie_file, collector_cookie_file


def getuid():

    proxies = {'http': None, 'https': None}
    lists = set()
    keywords = set()

    if os.path.exists(uid_file):
        print(f"文件 {uid_file} 存在，已删除。")
        os.remove(uid_file)
    else:
        print(f"文件 {uid_file} 不存在，无需删除。")

    cookies = pickle.load(open(reporter_cookie_file, "rb"))
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
    print(f'稍后再看：举报账号')
    headers = {'cookie': COOKIE, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=proxies,
                            timeout=(3, 3))
    print(response)
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        lists.add(str(mid))
        print(mid)

    data = {'csrf': CSRF}
    response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data,
                             proxies=proxies, timeout=(3, 3))
    print(response.text)

    cookies = pickle.load(open(collector_cookie_file, "rb"))
    COOKIE = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
    print(f'稍后再看：主号')
    headers = {'cookie': COOKIE, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=proxies,
                            timeout=(3, 3))
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        lists.add(str(mid))
        print(mid)

    data = {'csrf': CSRF}
    response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data,
                             proxies=proxies, timeout=(3, 3))
    print(response.text)

    with open(black_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            uid = line.strip()
            lists.add(uid)

    with open(white_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            uid = line.strip()
            lists.discard(uid)
    lists.discard("")
    sorted_lists = sorted(lists,key=int)
    with open(black_file, 'w', encoding='utf-8') as file:
        for sorted_list in sorted_lists:
            file.write(f'{sorted_list}\n')

    with open(keywords_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            keyword = line.strip()
            if keyword:  # 非空字符串才添加
                keywords.add(keyword)
    if keywords:
        for keyword in keywords:
            mids = set()
            headers = {'cookie': COOKIE, 'user-agent': UA}
            print(f"正在搜索关键词：{keyword}")
            response = requests.get(
                f'https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=video',
                headers=headers, proxies=proxies,
                timeout=(3, 3))
            data = response.json()

            for item in data.get("data", {}).get("result", []):
                mid = item.get("mid")
                if mid is not None:
                    lists.add(mid)
                    mids.add(mid)
                if len(mids) >=10:
                    break
            print(f"搜索结果：{mids}")

    lists.discard("")
    sorted_lists = sorted(lists, key=int)
    with open(uid_file, 'w', encoding='utf-8') as file:
        for sorted_list in sorted_lists:
            file.write(f'{sorted_list}\n')

    return "0"

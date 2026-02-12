import json
import requests
import re
import os

from variables import uid_file, black_file, white_file, keywords_file, UA, reporter_cookie_file, collector_cookie_file,timeout_request,proxies


def getuid():
    lists = set()
    keywords = set()

    if os.path.exists(uid_file):
        print(f"文件 {uid_file} 存在，已删除。")
        os.remove(uid_file)
    else:
        print(f"文件 {uid_file} 不存在，无需删除。")

    # ------------------ 获取Cookie ------------------
    with open(reporter_cookie_file, "r", encoding="utf-8") as f:
        storage = json.load(f)
    cookies = storage.get("cookies", [])
    reporter_cookie = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    reporter_csrf = re.search(r'bili_jct=([^;]*)', reporter_cookie).group(1)
    with open(collector_cookie_file, "r", encoding="utf-8") as f:
        storage = json.load(f)
    cookies = storage.get("cookies", [])
    collector_cookie = "; ".join(f"{c['name']}={c['value']}" for c in cookies)
    collector_csrf = re.search(r'bili_jct=([^;]*)', collector_cookie).group(1)
    # ------------------ 获取列表 ------------------
    print('稍后再看：举报账号')
    headers = {'cookie': reporter_cookie, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=proxies,timeout=timeout_request)
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        lists.add(str(mid))
        print(mid)
    print('稍后再看：采集账号')
    headers = {'cookie': collector_cookie, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers,timeout=timeout_request,proxies=proxies)
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        lists.add(str(mid))
        print(mid)



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
            headers = {'cookie': reporter_cookie, 'user-agent': UA}
            print(f"正在搜索关键词：{keyword}")
            response = requests.get(
                f'https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=video',headers=headers, proxies=proxies, timeout=timeout_request)
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

    # ------------------ 清空列表 ------------------
    headers = {'cookie': reporter_cookie, 'user-agent': UA}
    data_post = {'csrf': reporter_csrf}
    response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data_post,proxies=proxies, timeout=timeout_request)
    print(response.text)
    headers = {'cookie': collector_cookie, 'user-agent': UA}
    data_post = {'csrf': collector_csrf}
    response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data_post,proxies=proxies, timeout=timeout_request)
    print(response.text)

    return "0"

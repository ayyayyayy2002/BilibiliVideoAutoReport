from dotenv import load_dotenv
import requests
import re
import os
def getuid():
    base_dir = os.getcwd()

    white_file = os.path.join(base_dir, 'list', 'white')
    black_file = os.path.join(base_dir, 'list', 'black')
    keywords_file = os.path.join(base_dir, 'list', 'keyword')
    uid_file = os.path.join(base_dir, 'list', 'uid')
    env_file = os.path.join(base_dir, '.env')
    load_dotenv(dotenv_path=env_file)
    proxies = {'http': None, 'https': None}
    UA = os.getenv('UA')
    lists = set()
    keywords = set()

    if os.path.exists(uid_file):
        print(f"文件 {uid_file} 存在，已删除。")
        os.remove(uid_file)
    else:
        print(f"文件 {uid_file} 不存在，无需删除。")

    COOKIE = os.getenv('reporter')
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
    print(f'稍后再看：举报账号')
    headers = {'cookie': COOKIE, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=proxies,
                            timeout=(3, 3))
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        aid = item['aid']
        lists.add(str(mid))
        print(mid)

    data = {'csrf': CSRF}
    response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data,
                             proxies=proxies, timeout=(3, 3))
    print(response.text)

    COOKIE = os.getenv('collector')
    CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
    print(f'稍后再看：主号')
    headers = {'cookie': COOKIE, 'user-agent': UA}
    response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=proxies,
                            timeout=(3, 3))
    data = response.json()
    for item in data['data']['list']:
        mid = item['owner']['mid']
        aid = item['aid']
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

    with open(black_file, 'w', encoding='utf-8') as file:
        for list in lists:
            file.write(f'{list}\n')

    with open(keywords_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            keyword = line.strip()
            if keyword:  # 非空字符串才添加
                keywords.add(keyword)
    if keywords:
        for keyword in keywords:
            mids = set()
            COOKIE = os.getenv('reporter')
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



    with open(uid_file, 'w', encoding='utf-8') as file:
        for list in lists:
            file.write(f'{list}\n')

    return "0"

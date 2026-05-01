import json
import requests
import re
import os
import variables
def getuid():
    lists = set()
    keywords = set()

    if os.path.exists(variables.path.uid_file):
        print(f"文件 {variables.path.uid_file} 存在，已删除。")
        os.remove(variables.path.uid_file)
    cookies=None
    for i in range(0, variables.accountcount):
        with open(os.path.join(variables.path.cookie_path, f'{i}.json'), "r", encoding="utf-8") as f:
            storage = json.load(f)
        cookies = storage.get("cookies", [])
        # 只保留 domain 包含 .bilibili.com 的 cookie
        filtered = [c for c in cookies if ".bilibili.com" in c.get("domain", "")]
        cookies = "; ".join(f"{c['name']}={c['value']}" for c in filtered)
        print(f'稍后再看：账号{i}')
        headers = {'cookie': cookies, 'user-agent': variables.UA}
        response = requests.get('https://api.bilibili.com/x/v2/history/toview', headers=headers, proxies=variables.clash.proxy, timeout=variables.timeout.request)
        data = response.json()
        for item in data['data']['list']:
            mid = item['owner']['mid']
            lists.add(str(mid))
            print(mid)

    # ------------------ 合并黑白名单 ------------------
    for file_path in [variables.path.black_file, variables.path.white_file]:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                if file_path == variables.path.black_file:
                    lists.update(lines)
                else:
                    lists.difference_update(lines)

    sorted_lists = sorted(lists, key=int)
    with open(variables.path.black_file, 'w', encoding='utf-8') as f:
        for uid in sorted_lists:
            f.write(f'{uid}\n')

    # ------------------ 搜索关键词 ------------------
    if os.path.exists(variables.path.keyword_file):
        with open(variables.path.keyword_file, 'r', encoding='utf-8') as f:
            for line in f:
                keyword = line.strip()
                if keyword:
                    keywords.add(keyword)

    if keywords:
        for keyword in keywords:
            mids = set()
            headers = {'cookie': cookies, 'user-agent': variables}
            print(f"正在搜索关键词：{keyword}")
            response = requests.get(
                f'https://api.bilibili.com/x/web-interface/search/type?keyword={keyword}&search_type=video&order=pubdate',headers=headers, proxies=variables.clash.proxy, timeout=variables.timeout.request)
            data = response.json()
            for item in data.get("data", {}).get("result", []):
                mid = item.get("mid")
                if mid is not None:
                    lists.add(str(mid))
                    mids.add(str(mid))
                if len(mids) >= 30:
                    break
            print(f"搜索结果：{mids}")



    sorted_lists = sorted(lists, key=int)
    with open(variables.path.uid_file, 'w', encoding='utf-8') as f:
        for uid in sorted_lists:
            f.write(f'{uid}\n')

    # ------------------ 清空列表 ------------------
    for i in range(0, variables.accountcount):
        with open(os.path.join(variables.path.cookie_path, f'{i}.json'), "r", encoding="utf-8") as f:
            storage = json.load(f)
        cookies = storage.get("cookies", [])
        # 只保留 domain 包含 .bilibili.com 的 cookie
        filtered = [c for c in cookies if ".bilibili.com" in c.get("domain", "")]
        cookies = "; ".join(f"{c['name']}={c['value']}" for c in filtered)
        csrf = re.search(r'bili_jct=([^;]*)', cookies).group(1)
        headers = {'cookie': cookies, 'user-agent': variables.UA}
        data_post = {'csrf': csrf}
        response = requests.post('https://api.bilibili.com/x/v2/history/toview/clear', headers=headers, data=data_post, proxies=variables.clash.proxy, timeout=variables.timeout.request)
        print(response.text)



    return "0"

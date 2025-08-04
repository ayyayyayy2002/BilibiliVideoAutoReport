from dotenv import load_dotenv, set_key
from datetime import datetime
from Capcha import capcha
from AVtoBV import enc
import requests
import random
import re
import os

from Proxy import proxy

base_dir = os.path.dirname(os.path.abspath(__file__))
########################################################################################################################
uid_file = os.path.join(base_dir, 'list', 'uid')
env_file = os.path.join(base_dir, '.env')


#proxies = {'http': None, 'https': None}
clashproxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}
uids = set()
load_dotenv(dotenv_path=env_file)
UA = os.getenv('UA')

COOKIE = os.getenv("reporter")

CSRF = re.search(r'bili_jct=([^;]*)', COOKIE).group(1)
########################################################################################################################

tids_with_weights = {
    '2':1,  # 违法违禁
    '5':1,  # 赌博诈骗
    '10025':1,  # 违法信息外链
    '10014':30,#涉政谣言
    '10015':4,#涉社会事件谣言
    '10017':1,#虚假不实信息
    '10018':60,#违规推广
    '52':40,#转载/自制错误
    '10019':2,#其他不规范行为
    '7':1,#人身攻击
    '9':10,#引战
    '3':1,#色情低俗
    '10020':2,#危险行为
    '10021':1,#观感不适
    '6':1,#血腥暴力
    '10000':1,#青少年不良信息
    '10022':1,#其他
}
tids = list(tids_with_weights.keys())
weights = list(tids_with_weights.values())





try:
    with open(uid_file, 'r', encoding='utf-8') as file:  # 以读取模式打开文件
        for line in file:
            line = line.strip()  # 去掉行首尾的空白字符
            if line.isdigit():
                uids.add(line)
except Exception as e:
    print(f"无法读取UID文件: {e}")
    exit(0)

if not uids:
    print("uid.txt 文件中没有可处理的UID，程序退出")
    exit(0)

for uid in uids:
    date = datetime.now().strftime('[%m-%d]')
    aid_log_file = os.path.join(base_dir, 'record', 'report', f'{date}{uid}.txt')
    headers = {'cookie': COOKIE, 'user-agent': UA}
    search_url = f'https://api.bilibili.com/x/web-interface/card?mid={uid}'
    response = requests.get(search_url, headers=headers, proxies=clashproxies, timeout=(5, 10))
    #print(response.text)
    data = response.json()
    name = data['data']['card']['name']



    print(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}")
    with open(aid_log_file, 'a', encoding='utf-8') as file:
        file.write(f"UID: {uid} NAME: {name} TIME: {datetime.now().strftime('[%Y-%m-%d %H-%M-%S]')}3\n")

    aids = []
    titles = []
    pics = []





    search_url = f'https://api.bilibili.com/x/series/recArchivesByKeywords?mid={uid}&keywords=&ps=0'
    headers = {'cookie': COOKIE, 'user-agent': UA}
    response = requests.get(search_url, headers=headers, proxies=clashproxies, timeout=(3, 3))
    data = response.json()
    for archive in data['data']['archives']:
        aids.append(archive['aid'])
        titles.append(archive['title'])
        pics.append(archive['pic'])
    count = len(aids)
    print(f'普通视频个数:{count}')
    with open(aid_log_file, 'a', encoding='utf-8') as file:
        file.write(f"普通视频个数:{count}\n")




    length = len(aids)

    print(f'\nhttps://space.bilibili.com/{uid}\n')
    reportcount = 0


    for aid, title, pic in zip(aids, titles, pics):
        tid = random.choices(tids, weights=weights, k=1)[0]
        reportcount += 1
        #time.sleep(0.03)
        headers = {'cookie': COOKIE, 'user-agent': UA}
        #print(headers)
        data = {
            'aid': aid,
            'attach': pic,
            'block_author': 'false',
            'csrf': CSRF,
            'desc': f'在视频标题{title}中有违规行为',
            'tid': f'{tid}'
        }
        try:
            response = requests.post('https://api.bilibili.com/x/web-interface/appeal/v2/submit', headers=headers,data=data,
                                      proxies=clashproxies, timeout=(3, 3))
            print(f'视频{reportcount:03}:{response.text}')
            if "62009" in response.text or reportcount >= length-2 or reportcount >= 100:
                break
            elif "-352" in response.text or "-351" in response.text:
                COOKIE = capcha(aid)
                os.environ["reporter"] = COOKIE
                set_key(env_file, "reporter", COOKIE)



            elif "412" in response.text:
                proxy()
            print(f'视频{reportcount:03}:{response.text}')

            with open(aid_log_file, 'a', encoding='utf-8') as file:
                file.write(f'{enc(int(aid))},{tid}，{title}\n')
        except Exception:
            proxy()


    try:
        with open(uid_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(uid_file, 'w', encoding='utf-8') as f:
            for line in lines:
                if line.strip() != uid:
                    f.write(line)
        print(f"删除UID: {uid}")
    except Exception as e:
        print(f"删除UID时发生错误: {e}")





import json
import time
import requests
import sqlite3
from tqdm import tqdm
from utils_proxy import switch_proxy
from variables import black_file, timeout_request, proxies, reporter_cookie_file, UA, uid_sql


def uidsql():
    uids = []

    try:
        with open(black_file, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if line.isdigit():
                    uids.append(line)
    except Exception as e:
        print(f"无法读取UID文件: {e}")
        return "0"

    # 建立数据库连接（循环外）
    conn = sqlite3.connect(uid_sql)
    cursor = conn.cursor()

    updated = []
    added = []
    with open(reporter_cookie_file, "r", encoding="utf-8") as f:
        storage = json.load(f)
    cookies = storage.get("cookies", [])
    filtered = [c for c in cookies if ".bilibili.com" in c.get("domain", "")]
    reporter_cookie = "; ".join(f"{c['name']}={c['value']}" for c in filtered)

    headers = {'cookie': reporter_cookie, 'user-agent': UA}

    for uid in tqdm(uids):
        while True:
            try:
                response = requests.get(
                    f'https://api.bilibili.com/x/space/acc/info?mid={uid}',
                    proxies=proxies,
                    timeout=timeout_request,
                    headers=headers
                )
                #print(response.text)
                data = response.json()
                if data.get("code") != 0:
                    raise Exception(data)
                info = data.get("data", {})
                mid = info.get("mid")
                nickname = info.get("name")
                sign = info.get("sign")
                silence = info.get("silence")
                break
            except Exception as e:
                print(e)
                switch_proxy()
                time.sleep(1)

        if not mid:
            continue

        cursor.execute("SELECT nickname, silence, sign FROM record WHERE uid=?", (mid,))
        row = cursor.fetchone()

        if row:
            old_nickname, old_silence, old_sign = row

            if (old_nickname != nickname) or (old_silence != silence) or (old_sign != sign):
                cursor.execute(
                    "UPDATE record SET nickname=?, silence=?, sign=? WHERE uid=?",
                    (nickname, silence, sign, mid)
                )
                updated.append({
                    "mid": mid,
                    "old": (old_nickname, old_silence, old_sign),
                    "new": (nickname, silence, sign)
                })
        else:
            cursor.execute(
                "INSERT INTO record (uid, nickname, silence, sign) VALUES (?, ?, ?, ?)",
                (mid, nickname, silence, sign)
            )
            added.append({
                "uid": mid,
                "nickname": nickname,
                "silence": silence,
                "sign": sign
            })

        conn.commit()

    conn.close()

    print("\n新增记录：")
    for item in added:
        print(item)

    print("\n更新记录：")
    for item in updated:
        print(item)

    return "0"

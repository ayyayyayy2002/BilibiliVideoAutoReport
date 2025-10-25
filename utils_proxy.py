import requests

from variables import CLASH_API_URL


def switch_proxy(GROUP):


    # 获取 GLOBAL 策略组信息
    group_url = f"{CLASH_API_URL}/proxies/{GROUP}"
    response = requests.get(group_url)
    data = response.json()

    proxies = data.get("all", [])
    current_proxy = data.get("now")

    print("当前代理:", current_proxy)
    #print("所有可选代理:", proxies)

    # 去掉前两个和后五个（如果有必要）
    proxies = proxies[2:-6]
    # 去除空格、重复
    proxies = list(dict.fromkeys([p.strip() for p in proxies]))

    if not proxies:
        print("代理列表为空，无法切换。")
        return

    # 计算下一个代理（循环）
    try:
        index = proxies.index(current_proxy)
        next_index = 0 if index == len(proxies) - 1 else index + 1
    except ValueError:
        print("当前代理不在可选列表中，默认选择第一个。")
        next_index = 0

    next_proxy = proxies[next_index]
    print(f"切换到下一个代理: {next_proxy}")

    # 切换代理
    put_url = f"{CLASH_API_URL}/proxies/{GROUP}"
    res = requests.put(put_url, json={"name": next_proxy})
    if res.status_code == 204:
        print("代理切换成功！")

    # 关闭所有连接
    delete_url = f"{CLASH_API_URL}/connections"
    del_res = requests.delete(delete_url)
    if del_res.status_code == 204:
        print("连接清除成功！")

# 直接调用
if __name__ == "__main__":
    switch_proxy("哔哩哔哩")

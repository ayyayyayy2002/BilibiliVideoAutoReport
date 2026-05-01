import requests
import variables


def switch_proxy():
    headers = {"Authorization": f"Bearer {variables.clash.secret}"}

    # ====================== 1. 获取代理列表 ======================
    if variables.Global.proxy_list is None or len(variables.Global.proxy_list) == 0:
        print("正在从 Clash 获取代理列表...")
        try:
            group_url = f"{variables.clash.url_api}/group/{variables.clash.group}/delay?url=https://api.bilibili.com/&timeout=5000"
            response = requests.get(
                group_url,
                timeout=variables.timeout.request,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            variables.proxy_list = list(data.keys())

        except Exception as e:
            print(f"获取代理列表失败: {e}")
            return None, None

    if not variables.Global.proxy_list:
        print("代理列表为空，无法切换。")
        return None, None

    # ====================== 2. 确定要切换到的代理 ======================
    if variables.Global.proxy_current is None:
        next_proxy = variables.Global.proxy_list[0]
        print("未传入当前代理，默认切换到列表第一个代理")
    else:
        try:
            index = variables.Global.proxy_list.index(variables.Global.proxy_current)

            if index == len(variables.Global.proxy_list) - 1:
                print("当前代理是最后一个，重新获取代理列表...")

                try:
                    group_url = f"{variables.clash.url_api}/group/{variables.clash.group}/delay?url=https://api.bilibili.com/&timeout=5000"
                    response = requests.get(
                        group_url,
                        timeout=10,
                        headers=headers
                    )
                    response.raise_for_status()
                    data = response.json()

                    variables.proxy_list = list(data.keys())

                    if not variables.Global.proxy_list:
                        print("刷新后代理列表为空")
                        return None, None

                    next_proxy = variables.Global.proxy_list[0]

                except Exception as e:
                    print(f"刷新代理列表失败: {e}")
                    return None, None

            else:
                next_proxy = variables.Global.proxy_list[index + 1]

        except ValueError:
            print("当前代理不在列表中，默认切换到第一个代理")
            next_proxy = variables.Global.proxy_list[0]

    print(f"即将切换到: {next_proxy},代理总数: {len(variables.Global.proxy_list)}")

    # ====================== 3. 先切换代理 ======================
    print(f"正在切换代理到: {next_proxy}")
    put_url = f"{variables.clash.url_api}/proxies/{variables.clash.group}"
    res = requests.put(
        put_url,
        json={"name": next_proxy},
        headers=headers
    )

    if res.status_code == 204:
        print("代理切换成功！")
        variables.proxy_current = next_proxy
    else:
        print(f"代理切换失败，状态码: {res.status_code}")
        variables.proxy_list = None
        variables.proxy_current = None
        return None, None

    # ====================== 4. 再关闭指定 host 的连接 ======================
    print("正在关闭 host 包含 api.bili 的连接...")

    conn_url = f"{variables.clash.url_api}/connections"

    try:
        res = requests.get(
            conn_url,
            timeout=5,
            headers=headers
        )
        res.raise_for_status()
        data = res.json()
        connections = data.get("connections", [])

        for c in connections:
            host = c.get("metadata", {}).get("host", "")
            conn_id = c.get("id")

            if "bili" in host and conn_id:
                delete_url = f"{variables.clash.url_api}/connections/{conn_id}"
                del_res = requests.delete(
                    delete_url,
                    headers=headers
                )

                if del_res.status_code == 204:
                    print(f"已关闭连接: {conn_id}")
                else:
                    print(f"关闭失败: {conn_id}, 状态码: {del_res.status_code}")

    except Exception as e:
        print(f"获取或关闭连接失败: {e}")

    return None
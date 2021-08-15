# first line: 18
@memory.cache
def get_client(proxies: Union[str, dict] = None, verify: bool = False) -> httpx.Client:
    """Gen and cache a httpx.Client.

    Args:
        proxies: setup and persistant
    """
    # url = "https://translate.google.cn"
    headers = {
        # 'Referer': 'http://translate.google.cn/',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36',
        "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
    }

    if proxies is None:
        client = httpx.Client(verify=verify, headers=headers)
    else:
        client = httpx.Client(proxies=proxies, verify=verify, headers=headers)

    # client.event_hooks["response"] = [raise_on_4xx_5xx]
    # client.event_hooks["request"] = [log_request]
    # client.event_hooks["request"] = [add_timestamp]
    return client

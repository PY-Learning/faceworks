# -*- encoding: utf-8 -*-

import requests
import bs4
import time
import json


def jiayuan_api(page=1):
    header = {
        "Referer": "http://search.jiayuan.com/v2/index.php",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Origin": "http://search.jiayuan.com"
    }

    params = {
        "sex": "f",
        "key": "",
        "sn": "default",
        "sv": "1",
        "p": page,
        "f": "select",
        "listStyle": "bigPhoto",
        "pri_uid": "0",
        "jsversion": "v5",
        "stc": "2:20.40,23:1",
    }

    return requests.get('http://search.jiayuan.com/v2/search_v2.php',
                        params=params, headers=header).content.decode('utf-8')


def get_url(data):
    data = data[11:-13]
    d = json.loads(data)
    urls = [i['image'] for i in d['userInfo']]
    return urls


for i in range(20, 100):
    data = jiayuan_api(i)
    urls = get_url(data)
    print('Got page %d' % i)
    with open('urls2.txt', 'a') as f:
        f.write('\n'.join(urls) + '\n')
    time.sleep(10)

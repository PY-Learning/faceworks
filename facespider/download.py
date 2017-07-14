# -*- encoding: utf-8 -*-

import requests
import hashlib
from io import BytesIO
import time


def md5hash(bytes):
    hash = hashlib.md5(bytes)
    return hash.hexdigest()


def download_image(url: str):
    header = {
        "Referer": "http://search.jiayuan.com/v2/index.php",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "Origin": "http://search.jiayuan.com"
    }
    try:
        img = requests.get(url, headers=header, timeout=30).content
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
        print('Failed: %s' % url)
        return
    md5 = md5hash(img)
    suffix = url.rsplit('.')[-1]
    with open('imgs/%s.%s' % (md5, suffix), 'wb') as f:
        f.write(img)
    with open('download.log', 'a') as f:
        f.write(url + '\n')


def main():
    count = 0
    with open('urls.txt', 'r') as f:
        urls = f.read().splitlines()
    with open('download.log', 'r') as f:
        downloaded_urls = set(f.read().splitlines())
    l = len(urls)
    for url in urls:
        if url not in downloaded_urls:
            time.sleep(0.5)
            download_image(url)
        count += 1
        print('Finish %.2f %%' % (count * 100 / l,))

if __name__ == '__main__':
    main()

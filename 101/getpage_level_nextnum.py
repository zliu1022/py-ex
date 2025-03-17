#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import getq
from pymongo import MongoClient, ReturnDocument
import sys

#获取 level的下一题的url_no

base_url = "https://www.101weiqi.com/"

header = {
    'cookie':'csrftoken=ujJhAxo83Z5mg0oRfxtwC2BqgQ0nTjvdeQSBbm3XHqqCWOB9FHF78lqvPA3MF6Ct;sessionid=gbszfob6tjb67kscg6uytllqskcczewu',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}
import time
def req_url_retry(url, retry):
    global header
    start_t = time.time()
    ori = retry - 1
    while retry:
        try:
            retry = retry - 1
            #r = requests.get(url, headers=self.header)
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            continue
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            continue
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            continue
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
            continue

        if retry != ori:
            print('retry', ori-retry, 'times', url)
        end_t = time.time()
        print('req_url_retry cost {:5.2f}s'.format(end_t - start_t))
        return 0, r

    end_t = time.time()
    print('req_url_retry cost {:5.2f}s'.format(end_t - start_t))
    return 1, {}

def get_nextnum(url_level, url_no):
    global base_url
    level_url = base_url + '/' + url_level + '/' + url_no

    ret, resp = req_url_retry(level_url, 3)
    if ret != 0:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')

    # 1. 先找到 <ul class="breadcrumb">
    breadcrumb_ul = soup.find('ul', class_='breadcrumb')

    # 2. 在 breadcrumb_ul 范围内找 li.active，提取 q_num
    active_li = breadcrumb_ul.find('li', class_='active')
    q_num_text = active_li.text.strip()  # "第1001题"

    # 提取数字
    match = re.search(r'\d+', q_num_text)
    q_num = int(match.group()) if match else None

    # 3. 在 breadcrumb_ul 范围内找 "下 一 题" 按钮，提取 next_url
    next_link_element = breadcrumb_ul.find('a', id='nextq')
    next_url = next_link_element['href'] if next_link_element else None

    # 输出结果
    print(f'q_num: {q_num}')
    print(f'next_url: {next_url}')
    quit()

if __name__ == '__main__':
    prefix = ''
    url_level = "5D"
    url_no = "208941"

    get_nextnum(url_level, url_no)

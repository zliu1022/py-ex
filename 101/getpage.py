#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import getq
from pymongo import MongoClient, ReturnDocument
import sys
from config import site_name, base_url, db_name

#
# 获取level list，不需要登录
# 另存为csv
# 默认获取第一页
# 获取全部需要去掉break注释，get_content_level 中的遍历所有页面
# url_no列表，数组形式存放到level集合
# url_no列表，单个文档形式存放到grade集合

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

def get_data(base_url, level_str, n):
    url = base_url + level_str + "?page=" + str(n)

    ret, resp = req_url_retry(url, 3)
    if ret != 0:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    divs = soup.find_all('div', class_='col-md-2 col-xs-6 col-sm-3')
    data = []
    for div in divs:
        a = div.find('a')
        title = a.find('span', class_='warptext').text
        img_url = a.find('img')['src']
        problem_url = base_url + a['href']
        title_name = title.split()[0]
        #title_rate = title.split()[1]
        #data.append({'level': level_str, 'title': title_name, 'correct_rate': title_rate, 'url': problem_url, 'img_url': img_url})
        data.append(title_name[2:])
    return data

def get_pagenum(soup):
    ellipsis_element = soup.find('a', text='...')
    ellipsis_parent_element = ellipsis_element.parent
    last_page_parent_element = ellipsis_parent_element.find_next_sibling('li')
    last_page_element = last_page_parent_element.find('a')
    last_page = int(last_page_element.text)
    return last_page

def update_list(doc):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db['level']

    collection.create_index('level', unique=True)

    filter = {'level': doc['level']}
    old = collection.find_one_and_replace(
        filter=filter,
        replacement=doc,
        upsert=True,
        return_document=ReturnDocument.BEFORE  # 返回更新前的文档
    )

    if old:
        differences = getq.dict_diff(old, doc)
        if differences:
            print("以下字段已被更新：")
            for field, change in differences.items():
                print(f"{field}: 从 {change['old']} 更新为 {change['new']}")
        else:
            print("数据已存在，且无任何变化。")
    else:
        print("level集合，插入新文档。")

'''
输入 level_str 和 数组new_list
数组 new_list存放了很多 url_no
对于每一个 url_no
查询 grade集合中是否有对应的 url_no：
- 如果没有，则加入：{
    "level_str": level_str,
    "url_no": new_list的元素
}
- 如果有，而且 level_str不一致，则进行更新，并打印 url_no 从原来的level_str替换成新的
'''
def update_grade(level_str, new_list):
    new_list = []
    replace_list = []

    client = MongoClient("mongodb://localhost:27017/")  # 连接 MongoDB
    db = client[db_name]  # 选择数据库
    collection = db["grade"]  # 选择集合

    for url_no in new_list:
        existing_doc = collection.find_one({"url_no": url_no})

        if not existing_doc:
            # 如果 url_no 不存在，则插入新文档
            collection.insert_one({"level_str": level_str, "url_no": url_no})
            print(f"new {level_str} {url_no}")
            new_list.append(url_no)
        elif existing_doc["level_str"] != level_str:
            # 如果 url_no 存在但 level_str 不同，则更新并打印变化
            old_level_str = existing_doc["level_str"]
            collection.update_one({"url_no": url_no}, {"$set": {"level_str": level_str}})
            print(f"replace {old_level_str} {url_no} -> {level_str} {url_no}")
            replace_list.append(url_no)

    print(f'{level_str} new {len(new_list)} replace {len(replace_list)}')

    client.close()  # 关闭连接

def get_content_level(level_str):
    level_url = base_url + level_str

    ret, resp = req_url_retry(level_url, 3)
    if ret != 0:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    pagenum = get_pagenum(soup)
    print(level_str, 'total_page', pagenum)

    all_data = []
    for i in range(1, pagenum+1):
        data = get_data(base_url, level_str, i)
        if data == None:
            continue
        all_data.extend(data)

    df = pd.DataFrame(all_data)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', None):
        print(df.head())
    print(f'total {len(df.index)}')

    level_content_filename = level_str + ".csv"
    df.to_csv(level_content_filename, index=False)

    doc = {
        'level': level_str,
        'list':  all_data
    }
    update_list(doc)

    #反复拿level的列表
    update_grade(level_str, all_data)

if __name__ == '__main__':
    level_str = "9K"
    if len(sys.argv) == 2:
        level_str = sys.argv[1]
    get_content_level(level_str)


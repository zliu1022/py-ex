#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from pymongo import UpdateOne
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import sys

from getq_v1 import get_url_v1, login, inc_getqnum
from getonebook_cover_content_v1 import getonebook_cover_content_onepage
from getonebook_cover_v1 import getonebook_cover_v1

from pprint import pprint
import time
import random

from config import site_name, base_url, cache_dir, db_name

'''
## 更新cover_content
- 输入book_n，book_id
- 在数据库book_n获取book_id的content
	- 拿到url，组成完整网页
	- 抓取网页
	- 解析cover_content，和下一页
	- 加入数据库批操作
		- 抓取下一页，直到完成
- 批操作数据库book_n_q
'''

def batch_update(ret, book_n, book_url_id, book_complete_url):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col = db[f'book_{book_n}_q']

    operations = []
    for item in ret:
        operations.append(
            UpdateOne(
                { 'book_id': book_url_id, 'url_no': item['url_no'], 'url_frombook': item['url_frombook'] },
                { '$set': { 'url_level': item['url_level'] } },
                upsert=True
            )
        )
    op_num = len(operations)
    if operations:
        result = book_q_col.bulk_write(operations)
        print(f"匹配 {result.matched_count}, 修改 {result.modified_count}, 新增 {result.upserted_count} {book_complete_url}")
    else:
        print(f'Warning: no operation, empty page {book_complete_url}')
    return op_num

def getonebook_cover_content(session, book_n, book_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_col = db[f'book_{book_n}']
    book_q_col = db[f'book_{book_n}_q']

    doc = book_col.find_one({'id': book_id})
    if not doc:
        return

    book_cover_url = base_url + '/book/' + str(book_id) + '/'
    print('cover_url', book_n, book_id, book_cover_url)
    response = get_url_v1(session, book_cover_url)
    if response.status_code == 200:
        ret, ret_q = getonebook_cover_v1(response.text)
    else:
        print('FAIL get_url', response.status_code, book_cover_url)
        print(response)
        return 1

    if ret != 0:
        print('FAIL getonebook_cover', ret)
        return 2
    book_col.update_one(
        {'id': book_id},
        {'$set': {
            'cover': ret_q.get('cover')
        }}
    )

    doc = book_col.find_one({'id': book_id})
    book_content = doc.get('cover', {}).get('content', [])

    for content in book_content:
        book_url = content['url']

        #第一次不跳过
        # 有可能抓取了一部份退出，重新抓取可以跳过这部份，content的url可以部份匹配url_frombook
        #ret = book_q_col.find_one({'url_frombook': {'$regex': book_url} })
        #if ret:
        #    continue

        batch_data = []
        next_pagenum = 1
        while next_pagenum != 0:
            book_complete_url = base_url + book_url + '?page=' + str(next_pagenum)
            print(book_n, book_id, book_complete_url)
            response = get_url_v1(session, book_complete_url)
            if response is None:
                print(f'fail to get cover {book_complete_url}')
                continue
            next_pagenum, data = getonebook_cover_content_onepage(response.text)

            batch_data.extend(data)

        if batch_data:
            op_num = batch_update(batch_data, book_n, book_id, book_complete_url)
        else:
            print(f'fail to decode {book_complete_url}')

    return 0

def getbook_cover_content(session, book_n):
    db = client[db_name]
    book_col = db[f'book_{book_n}']
    book_q_col = db[f'book_{book_n}_q']

    new_ids = sorted(book_col.distinct('id'))
    existing_ids = sorted(book_q_col.distinct('book_id'))

    #ids = set(new_ids) - set(existing_ids)
    print(f'book_{book_n} {len(new_ids)}ids book_{book_n}_q {len(existing_ids)}')

    print('book_id:', new_ids[0], new_ids[len(new_ids)-1])
    total_len = len(new_ids)
    
    cur = 0
    code_1 = []
    code_2 = []
    for book_id in new_ids:
        cur += 1

        print(f'{book_id} {cur}/{total_len}')
        ret = getonebook_cover_content(session, book_n, book_id)
        if ret == 1:
            code_1.append(book_id)
        elif ret == 2:
            code_2.append(book_id)
        else:
            pass

    print('book', book_n)
    print('code_1(get fail)  ', code_1)
    print('code_2(not public)', code_2)

if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    if len(sys.argv) == 4:
        username = sys.argv[1]
        book_n = int(sys.argv[2])
        book_id = int(sys.argv[3])
        session = login(client, username)
        if session is None:
            print("登录失败")
        getonebook_cover_content(session, book_n, book_id)
    elif len(sys.argv) == 3:
        username = sys.argv[1]
        book_n = int(sys.argv[2])
        session = login(client, username)
        if session is None:
            print("登录失败")
        getbook_cover_content(session, book_n)
    else:
        quit()


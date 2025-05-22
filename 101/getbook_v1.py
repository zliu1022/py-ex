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

from getq import get_url, login, inc_getqnum
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
- 原来的“按难度排序”可以根据最后字符串是否重复，重复的设置为404
'''

def batch_update(ret, book_n, book_url_id, book_complete_url):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col_404 = db[f'book_{book_n}_q_404']

    book_q_col_404.create_index([('url_frombook', 1), ('book_id', 1)], unique=True)

    operations = []
    for item in ret:
        operations.append(
            UpdateOne(
                { 'book_id': book_url_id, 'url_frombook': item['url_frombook'] },
                { '$set': { 'url_no': item['url_no'], 'url_level': item['url_level'] } },
                upsert=True
            )
        )
    op_num = len(operations)
    if operations:
        result = book_q_col_404.bulk_write(operations)
        print(f"匹配 {result.matched_count}, 修改 {result.modified_count}, 新增 {result.upserted_count} {book_complete_url}")
    else:
        print(f'Warning: no operation, empty page {book_complete_url}')
    return op_num

def getonebook_cover_content(session, book_n, book_id):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_col = db[f'book_{book_n}']
    book_q_col_404 = db[f'book_{book_n}_q_404']

    doc = book_col.find_one({'id': book_id})
    if not doc:
        return

    book_cover_url = base_url + '/book/' + str(book_id) + '/'
    print('cover_url', book_n, book_id, book_cover_url)
    response = get_url(session, book_cover_url)
    if response:
        ret, ret_q = getonebook_cover_v1(response.text)

    book_col.update_one(
        {'id': book_id},
        {'$set': {
            'chapters': ret_q.get('chapters'),
            'cover': ret_q.get('cover')
        }}
    )

    doc = book_col.find_one({'id': book_id})
    book_content = doc.get('cover', {}).get('content', [])

    for content in book_content:
        book_url = content['url']

        # 有可能抓取了一部份推出，重新抓取可以跳过这部份，content的url可以部份匹配url_frombook
        ret = book_q_col_404.find_one({'url_frombook': {'$regex': book_url} })
        if ret:
            print(f'skip {book_url}')
            continue

        batch_data = []
        next_pagenum = 1
        while next_pagenum != 0:
            book_complete_url = base_url + book_url + '?page=' + str(next_pagenum)
            print(book_n, book_id, book_complete_url)
            response = get_url(session, book_complete_url)
            if response is None:
                print(f'fail to get cover {book_complete_url}')
                continue
            next_pagenum, data = getonebook_cover_content_onepage(response.text)

            batch_data.extend(data)

        if batch_data:
            op_num = batch_update(batch_data, book_n, book_id, book_complete_url)
        else:
            print(f'fail to decode {book_complete_url}')

def getbook_cover_content(session, book_n):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_col = db[f'book_{book_n}']
    book_q_col = db[f'book_{book_n}_q']
    book_q_col_404 = db[f'book_{book_n}_q_404']

    # status 404 而且url_frombook中有"/0/"的book
    total_books_st_404_url0_not_in_set = set()
    docs = book_q_col.find({'status':404, 'url_frombook':{'$regex':'/0/'}}, {'book_id': 1})
    for doc in docs:
        total_books_st_404_url0_not_in_set.add(doc.get('book_id'))

    for book_id in total_books_st_404_url0_not_in_set:
        getonebook_cover_content(session, book_n, book_id)

if __name__ == "__main__":
    if len(sys.argv) == 4:
        username = sys.argv[1]
        book_n = int(sys.argv[2])
        book_id = int(sys.argv[3])
        session = login(username)
        if session is None:
            print("登录失败")
        getonebook_cover_content(session, book_n, book_id)
    elif len(sys.argv) == 3:
        username = sys.argv[1]
        book_n = int(sys.argv[2])
        session = login(username)
        if session is None:
            print("登录失败")
        getbook_cover_content(session, book_n)
    else:
        quit()


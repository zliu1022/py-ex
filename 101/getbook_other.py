#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
from pymongo import UpdateOne, MongoClient
import sys
import time
import random

from getq_v1 import get_url_v1, login, inc_getqnum
from getotherbook_content import getotherbook_content
from config import site_name, base_url, cache_dir, db_name

book_list = [
    {'name': 'chizi',    'book_url': '/question/chizi/'},
    {'name': 'guanzi',   'book_url': '/question/guanzi/'},
    {'name': 'buju',     'book_url': '/question/buju/'},
    {'name': 'qili',     'book_url': '/question/qili/'},
    {'name': 'zhongpan', 'book_url': '/question/zhongpan/'},
    {'name': 'pianzhao', 'book_url': '/question/pianzhao/'},
    {'name': 'shizhan',  'book_url': '/question/shizhan/'},

    {'name': '13', 'book_url': '/size/13/'},
    {'name': '11', 'book_url': '/size/11/'},
    {'name': '9',  'book_url': '/size/9/'},
    {'name': '8',  'book_url': '/size/8/'},
    {'name': '7',  'book_url': '/size/7/'},
    {'name': '6',  'book_url': '/size/6/'},
    {'name': '5',  'book_url': '/size/5/'},
    {'name': '4',  'book_url': '/size/4/'},

    #'name': '9K',  'book_url': '/9K/',
    #['15K', '14K', '13K', '12K', '11K', '10K', '9K', '8K', '7K', '6K', '5K', '4K', '3K', '2K', '1K', '1D', '2D', '3D', '4D', '5D', '6D', '7D']，

    #'name': 'clone',  'book_url': '/clone/'
]

def batch_update(ret, book_name, book_complete_url):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col = db[f'{book_name}']

    operations = []
    for item in ret:
        operations.append(
            UpdateOne(
                { 'url_no': item['url_no'] },
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

def _getbookurl(book_name):
    for b in book_list:
        if b.get('name') == book_name:
            return b.get('book_url')
    return None

def getbook_other_content(session, book_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col = db[f'{book_name}']

    book_url = _getbookurl(book_name)

    batch_data = []
    next_pagenum = 1
    while next_pagenum != 0:
        book_complete_url = base_url + book_url + '?page=' + str(next_pagenum)
        print(book_name, book_complete_url)
        response = get_url_v1(session, book_complete_url)
        if response is None:
            print(f'fail to get cover {book_complete_url}')
            continue
        next_pagenum, data = getotherbook_content(response.text)

        batch_data.extend(data)

    if batch_data:
        op_num = batch_update(batch_data, book_name, book_complete_url)
    else:
        print(f'fail to decode {book_complete_url}')

    return 0

from pprint import pprint
if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    if len(sys.argv) == 3:
        username = sys.argv[1]
        book_name = sys.argv[2]
        session = login(client, username)
        if session is None:
            print("登录失败")
        getbook_other_content(session, book_name)
    else:
        pprint(book_list)


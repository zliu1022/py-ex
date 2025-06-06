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
    {'name': 'chizi',    'book_url': '/question/chizi/',    'path_type':'question', 'level':""},
    {'name': 'guanzi',   'book_url': '/question/guanzi/',   'path_type':'question', 'level':""},
    {'name': 'buju',     'book_url': '/question/buju/',     'path_type':'question', 'level':""},
    {'name': 'qili',     'book_url': '/question/qili/',     'path_type':'question', 'level':""},
    {'name': 'zhongpan', 'book_url': '/question/zhongpan/', 'path_type':'question', 'level':""},
    {'name': 'pianzhao', 'book_url': '/question/pianzhao/', 'path_type':'question', 'level':""},
    {'name': 'shizhan',  'book_url': '/question/shizhan/',  'path_type':'question', 'level':""},

    {'name': '13', 'book_url': '/size/13/','path_type': 'size', 'level':""},
    {'name': '11', 'book_url': '/size/11/','path_type': 'size', 'level':""},
    {'name': '9',  'book_url': '/size/9/', 'path_type': 'size', 'level':""},
    {'name': '8',  'book_url': '/size/8/', 'path_type': 'size', 'level':""},
    {'name': '7',  'book_url': '/size/7/', 'path_type': 'size', 'level':""},
    {'name': '6',  'book_url': '/size/6/', 'path_type': 'size', 'level':""},
    {'name': '5',  'book_url': '/size/5/', 'path_type': 'size', 'level':""},
    {'name': '4',  'book_url': '/size/4/', 'path_type': 'size', 'level':""},

    {'name': 'clone',  'book_url': '/clone/', 'path_type': 'clone', 'level':""},

    #['15K', '14K', '13K', '12K', '11K', '10K', '9K', '8K', '7K', '6K', '5K', '4K', '3K', '2K', '1K', '1D', '2D', '3D', '4D', '5D', '6D', '7D']，
    {'name': '15K',  'book_url': '/15K/', 'path_type': 'level', 'level':"15K"},
    {'name': '14K',  'book_url': '/14K/', 'path_type': 'level', 'level':"14K"},
    {'name': '13K',  'book_url': '/13K/', 'path_type': 'level', 'level':"13K"},
    {'name': '12K',  'book_url': '/12K/', 'path_type': 'level', 'level':"12K"},
    {'name': '11K',  'book_url': '/11K/', 'path_type': 'level', 'level':"11K"},
    {'name': '10K',  'book_url': '/10K/', 'path_type': 'level', 'level':"10K"},
    {'name': '9K',  'book_url': '/9K/', 'path_type': 'level', 'level':"9K"},
    {'name': '8K',  'book_url': '/8K/', 'path_type': 'level', 'level':"8K"},
    {'name': '7K',  'book_url': '/7K/', 'path_type': 'level', 'level':"7K"},
    {'name': '6K',  'book_url': '/6K/', 'path_type': 'level', 'level':"6K"},
    {'name': '5K',  'book_url': '/5K/', 'path_type': 'level', 'level':"5K"},
    {'name': '4K',  'book_url': '/4K/', 'path_type': 'level', 'level':"4K"},
    {'name': '3K',  'book_url': '/3K/', 'path_type': 'level', 'level':"3K"},
    {'name': '2K',  'book_url': '/2K/', 'path_type': 'level', 'level':"2K"},
    {'name': '1K',  'book_url': '/1K/', 'path_type': 'level', 'level':"1K"},
    {'name': '1D',  'book_url': '/1D/', 'path_type': 'level', 'level':"1D"},
    {'name': '2D',  'book_url': '/2D/', 'path_type': 'level', 'level':"2D"},
    {'name': '3D',  'book_url': '/3D/', 'path_type': 'level', 'level':"3D"},
    {'name': '4D',  'book_url': '/4D/', 'path_type': 'level', 'level':"4D"},
    {'name': '5D',  'book_url': '/5D/', 'path_type': 'level', 'level':"5D"},
    {'name': '6D',  'book_url': '/6D/', 'path_type': 'level', 'level':"6D"},
    {'name': '7D',  'book_url': '/7D/', 'path_type': 'level', 'level':"7D"},
]

def batch_update(ret, book_name, book_complete_url):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col = db[f'{book_name}']

    operations = []
    for item in ret:
        operations.append(
            UpdateOne(
                { 'url_no': item['url_no'], 'url_frombook': item['url_frombook'] },
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

def _getbook_path_type(book_name):
    for b in book_list:
        if b.get('name') == book_name:
            return b.get('path_type')
    return None

def _getbook_level(book_name):
    for b in book_list:
        if b.get('name') == book_name:
            return b.get('level')
    return None

def getbook_other_content(session, book_name):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col = db[f'{book_name}']

    book_url = _getbookurl(book_name)

    batch_data = []
    next_pagenum = 1
    print(book_name, book_url, end=' ')
    while next_pagenum != 0:
        book_complete_url = base_url + book_url + '?page=' + str(next_pagenum)
        print(next_pagenum, end=' ')
        response = get_url_v1(session, book_complete_url)
        if response is None:
            print(f'fail to get cover {book_complete_url}')
            continue
        next_pagenum, data = getotherbook_content(response.text, _getbook_path_type(book_name), _getbook_level(book_name))

        batch_data.extend(data)
    print()

    if batch_data:
        # 插入 path_type对应的表格
        op_num = batch_update(batch_data, _getbook_path_type(book_name), book_complete_url)
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
        if book_name == 'all':
            for b in book_list:
                getbook_other_content(session, b.get('name'))
        else:
            getbook_other_content(session, book_name)
    else:
        pprint(book_list)


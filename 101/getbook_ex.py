#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
from pymongo import MongoClient
from getonebook_cover_content_v1 import getonebook_cover_content_onepage
from getbook_v1 import batch_update
import sys
from getq_v1 import get_url_v1, login, inc_getqnum
from pprint import pprint
from config import site_name, base_url, cache_dir, db_name

ex_json = {
    'books':
        [{'id': 41653, 'name': '围棋练习册 入门篇（上）', 'nodecount': 0},
         {'id': 41654, 'name': '围棋练习册 入门篇（中）', 'nodecount': 0},
         {'id': 41655, 'name': '围棋练习册 入门篇（下）', 'nodecount': 0},
         {'id': 42156, 'name': '围棋练习册 初级篇（上）', 'nodecount': 0},
         {'id': 42163, 'name': '围棋练习册 初级篇（中）', 'nodecount': 0},
         {'id': 42175, 'name': '围棋练习册 初级篇（下）', 'nodecount': 0},
         {'id': 42907, 'name': '围棋练习册 中级篇（上）', 'nodecount': 0},
         {'id': 42908, 'name': '围棋练习册 中级篇（中）', 'nodecount': 0},
         {'id': 42909, 'name': '围棋练习册 中级篇（下）', 'nodecount': 0},
         {'id': 42920, 'name': '围棋练习册 高级篇（上）', 'nodecount': 0},
         {'id': 42921, 'name': '围棋练习册 高级篇（中）', 'nodecount': 0},
         {'id': 42922, 'name': '围棋练习册 高级篇（下）', 'nodecount': 0},
         {'id': 42983, 'name': '专项练习册-从15K到14K', 'nodecount': 659},
         {'id': 42984, 'name': '专项练习册-从13K到12K', 'nodecount': 600},
         {'id': 42985, 'name': '专项练习册-从11K到10K', 'nodecount': 689},
         {'id': 42986, 'name': '专项练习册-从9K到8K', 'nodecount': 599},
         {'id': 42987, 'name': '专项练习册-从7K到6K', 'nodecount': 600},
         {'id': 42988, 'name': '专项练习册-从5K到4K', 'nodecount': 680},
         {'id': 42989, 'name': '专项练习册-从3K到2K', 'nodecount': 560},
         {'id': 42990, 'name': '专项练习册-从1K到1D', 'nodecount': 659},
         {'id': 42991, 'name': '专项练习册-从2D到3D', 'nodecount': 650},
         {'id': 42992, 'name': '专项练习册-从4D到5D', 'nodecount': 800}]
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'zh,en;q=0.9,zh-CN;q=0.8',
    'Authorization': 'JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ4NTgxNTAwLCJpYXQiOjE3NDg0OTUxMDAsIkpXVCI6IjdkYmRmYTg4YzMwYzQ3MDc4ZWNkNjVjMTlhNThjNTM0IiwidXNlcl9pZCI6MjI3NjU3OX0.hj0TOXCKE0kI7QfEeeGoiBa3DQOp0h9nU9U2PLkmZPo',
    'Cache-Control': 'no-cache',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cookie': 'HMACCOUNT=74D1C63BE1C94EB5; Hm_lvt_13a338d58a330cc6f97cd0c32cf6dd47=1744191043; Hm_lpvt_13a338d58a330cc6f97cd0c32cf6dd47=1745818336; csrftoken=yAaObsfkLFJ3eqTbYKwde8MDn7QjYmpX; sessionid=siz998q6xeic7pna9qo1ni7wdgc5l10r',
    'DNT': '1',
    'Pragma': 'no-cache',
    'Referer': base_url + '/newbook/',
    'Sec-CH-UA': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
    'Sec-CH-UA-Mobile': '?0',
    'Sec-CH-UA-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Priority': 'u=1, i',
}

def getbook_cover_ex(session, no):
    url = base_url + '/jwt/getnewbookinfo/' + str(no) + '/'
    response = requests.get(url, headers=headers)
    print(url)
    print(response.status_code)
    ret_json = json.loads(response.text)
    obj = ret_json.get('book')

    result = {}

    result['id'] = obj.get('id')
    result['username'] = obj.get('username')
    result['name'] = obj.get('name')
    result['desc'] = obj.get('desc')
    result['desctext'] = obj.get('desctext')
    result['nodecount'] = obj.get('nodecount')
    result['chapters'] = obj.get('chapters')

    book_content = []
    book_id = result['id']
    count = 1
    for ch in result['chapters']:
        book_content.append({
            'url': f'/book/{book_id}/{ch.get('id')}',
            'no': count,
            'name': ch.get('name'),
            'num': ch.get('nodecount')
        })
        subcount = count*10 + 1
        for subch in ch.get('subs'):
            book_content.append({
                'url': f'/book/{book_id}/{subch.get('id')}',
                'no': subcount,
                'name': subch.get('name'),
                'num': subch.get('nodecount')
            })
            subcount += 1
        count += 1
        
    result['cover'] = { 'content': book_content}

    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_col = db[f'book_ex']
    book_q_col = db[f'book_ex_q']
    book_col.insert_one(result)

    doc = book_col.find_one({'id': book_id})
    book_content = doc.get('cover', {}).get('content', [])

    for content in book_content:
        book_url = content['url']

        batch_data = []
        next_pagenum = 1
        while next_pagenum != 0:
            book_complete_url = base_url + book_url + '?page=' + str(next_pagenum)
            print(book_id, book_complete_url)
            response = get_url_v1(session, book_complete_url)
            if response is None:
                print(f'fail to get cover {book_complete_url}')
                continue
            next_pagenum, data = getonebook_cover_content_onepage(response.text)

            batch_data.extend(data)

        if batch_data:
            op_num = batch_update(batch_data, 'ex', book_id, book_complete_url)
        else:
            print(f'fail to decode {book_complete_url}')

    return 0


if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    if len(sys.argv) == 3:
        username = sys.argv[1]
        book_id = int(sys.argv[2])
        session = login(client, username)
        if session is None:
            print("登录失败")
        getbook_cover_ex(session, book_id)
    else:
        pprint(ex_json)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from getq_v1 import login, getq_url_frombook, inc_getqnum
import time
import random
import sys
from config import db_name, base_url

def wait_qcounter(counter, rest_num=150):
    counter += 1
    if counter == 125:
        wait_time = 300
        print(f"Reached 125 calls to getq. Waiting for {wait_time} seconds")
        time.sleep(wait_time)
        counter = 0
    else:
        wait_time = random.randint(15, 30)
        print(f"Waiting for {wait_time} seconds.")
        time.sleep(wait_time)
    return counter

def getdb_bookid(client, username, book_str, book_id):
    session = login(client, username)
    if session is None:
        print("登录失败")
        return

    start_t = time.time()
    code_1_list = []  # 获取页面失败
    getq_counter = 0

    db = client[db_name]
    book_collection = db[book_str]
    documents = book_collection.find({'book_id': book_id}, {'_id': 0, 'url_frombook': 1}).sort('url_frombook', 1)
    if documents is None:
        print(f"No document found with {book_id}")
        return
    data_list = [doc.get('url_frombook') for doc in documents]
    print(f'bookid {book_id} {len(data_list)} urls')

    q_collection = db['q']
    cur_no = 0
    for url_frombook in data_list:
        ret = q_collection.find_one({
            'url_frombook': url_frombook,
            'status': {'$ne': 404}
        })
        if ret:
            print(f'{url_frombook} 已经存在')
            continue

        cur_no += 1
        print(f'{book_str} {book_id} {url_frombook} {cur_no}th')
        result = getq_url_frombook(client, session, url_frombook)
        inc_getqnum(client, username)

        if result.get('ret') == False:
            code = result.get('code')
            if code == 1:
                code_1_list.append(url_frombook)
        getq_counter = wait_qcounter(getq_counter)

    end_t = time.time()
    print("获取页面失败（code=1）列表：", code_1_list)
    print(f'{cur_no} done')
    print('cost {:5.2f}s'.format(end_t - start_t))

def getdb_book(username, book_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_collection = db[book_str]

    documents = book_collection.distinct('book_id')
    if documents:
        data_list = list(documents)
        print(f'{book_str} {len(data_list)} books')

        getdb_bookid(client, username, book_str, 3764)
        quit()

        for book_id in data_list:
            getdb_bookid(client, username, book_str, book_id)
    else:
        print(f"No document found with {book_str}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        username = sys.argv[1]
        book_str = 'book_' + sys.argv[2] + '_q'
    else:
        quit()
    getdb_book(username, book_str)
    print(username, book_str, 'done')


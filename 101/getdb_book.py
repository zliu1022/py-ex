#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from getq_v1 import login, getq_url_frombook, inc_getqnum
import time
import random
import sys
from config import db_name, base_url
from datetime import datetime
from ip import SourceIPAdapter

def wait_qcounter(counter, rest_num=150):
    counter += 1
    if counter == 1500:
        wait_time = 8*3600
        print(f"Reached 1500. Waiting for {wait_time}s")
        time.sleep(wait_time)
    if counter % 125 == 0:
        wait_time = 300
        print(f"Reached 125. Waiting for {wait_time}s")
        time.sleep(wait_time)
        counter = 0
    else:
        wait_time = random.randint(15, 90)
        print(f"... {wait_time}s")
        time.sleep(wait_time)
    return counter

def getdb_bookid(client, source_ip, username, book_str, book_id):
    session = login(client, username)
    if session is None:
        print("登录失败")
        quit()
        return
    adapter = SourceIPAdapter(source_ip)
    session.mount('http://', adapter)
    session.mount('https://', adapter)

    start_t = time.time()
    code_1_list = []  # 获取页面失败
    code_2_list = []  # 不共享
    getq_counter = 0

    db = client[db_name]
    book_q_str = 'book_' + book_str + '_q'
    book_q_collection = db[book_q_str]

    # 找到book_id，没成功抓取的url_frombook
    documents = book_q_collection.find({'book_id': book_id, 'status': { '$ne': 2 }}, {'_id': 0, 'url_frombook': 1}).sort('url_frombook', 1)
    data_list = [doc.get('url_frombook') for doc in documents]
    if len(data_list) == 0:
        print(f"No document found with {book_id}")
        return
    print(f'bookid {book_id} {len(data_list)} urls (status!=2) ')

    # 在book库，锁定book_id
    book_collection = db["book_" + book_str]
    result = book_collection.update_one({'id': book_id}, {'$set': {'status': 'doing'}})
    print(f"book_{book_str} id {book_id}: doing/LOCKED!!! {result}")

    cur_no = 0
    for url_frombook in data_list:
        cur_no += 1
        #print(f'{book_q_str} {book_id} {url_frombook} {cur_no}th')
        print(f'{url_frombook} {cur_no}th')
        result = getq_url_frombook(client, session, book_q_str, url_frombook)
        inc_getqnum(client, username)

        if result.get('ret') == False:
            code = result.get('code')
            if code == 1:
                code_1_list.append(url_frombook)
            if code == 2:
                code_2_list.append(url_frombook)
        getq_counter = wait_qcounter(getq_counter)

    result = book_collection.update_one({'id': book_id}, {'$set': {'status': 'ok'}})
    print(f"book_{book_str} id {book_id}: ok {result}")

    end_t = time.time()
    print("获取页面失败（code=1）列表：", code_1_list)
    print("不共享      （code=2）列表：", code_2_list)
    print(f'book_{book_str} id {book_id} {cur_no} done')
    print('cost {:5.2f}s'.format(end_t - start_t))
    print('------------------------------------------------------------')

def getdb_book(source_ip, username, book_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_collection = db["book_" + book_str]

    # book中 跳过：doing正在抓，ok抓完
    query = {
        '$or': [
            {'status': {'$exists': False}},
            {'status': {'$nin': ['ok', 'doing']}}
        ]
    }
    documents = book_collection.find(query, {'id': 1, '_id': 0})
    data_list = [doc.get('id') for doc in documents]

    while len(data_list) != 0:
        now = datetime.now()
        print(now.strftime("%Y-%m-%d %H:%M:%S"))

        print(f'book_{book_str} {len(data_list)} books')
        book_id = data_list[0]
        print(f'book_{book_str} id {book_id} idle')
        getdb_bookid(client, source_ip, username, book_str, book_id)

        time.sleep(random.randint(30, 120))
        query = {
            '$or': [
                {'status': {'$exists': False}},
                {'status': {'$nin': ['ok', 'doing']}}
            ]
        }
        documents = book_collection.find(query, {'id': 1, '_id': 0})
        data_list = [doc.get('id') for doc in documents]

if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    if len(sys.argv) == 6:
        source_ip = sys.argv[1]
        username = sys.argv[2]
        book_str = sys.argv[3]
        book_id = int(sys.argv[4])
        url_frombook = sys.argv[5]

        session = login(client, username)
        if session is None:
            print("登录失败")
            quit()
        adapter = SourceIPAdapter(source_ip)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        # get one url_frombook
        book_q_str = 'book_' + book_str + '_q'
        result = getq_url_frombook(client, session, book_q_str, url_frombook)
        inc_getqnum(client, username)
        print('getdb url_frombook', username, book_str, book_id, url_frombook, 'done')
    elif len(sys.argv) == 5:
        source_ip = sys.argv[1]
        username = sys.argv[2]
        book_str = sys.argv[3]
        book_id = int(sys.argv[4])

        # get one book_id
        getdb_bookid(client, source_ip, username, book_str, book_id)
        print('getdb bookid', username, book_str, book_id, 'done')
    elif len(sys.argv) == 4:
        source_ip = sys.argv[1]
        username = sys.argv[2]
        book_str = sys.argv[3]

        # get one book
        getdb_book(source_ip, username, book_str)
        print('getdb book', username, book_str, 'done')
    else:
        print('getdb_book.py source_ip username book_str book_id url_frombook')
        print('getdb_book.py source_ip username book_str book_id')
        print('getdb_book.py source_ip username book_str: choose idle id to get')
        quit()


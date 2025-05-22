#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from getq_v1 import login, getq_url_frombook, inc_getqnum, getq_url_frombook_from_q
import time
import random
import sys
from config import db_name, base_url
from datetime import datetime, timedelta
from ip import SourceIPAdapter

def sleep_until_next_day_9am():
    now = datetime.now()
    # 定义当天的晚上10点
    today_10pm = now.replace(hour=22, minute=30, second=0, microsecond=0)

    if now >= today_10pm:
        # 定义第二天早上6点
        next_day_6am = (today_10pm + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
        # 计算需要休眠的秒数
        sleep_seconds = (next_day_6am - now).total_seconds() + random.randint(300, 600)
        print(f"{now.strftime('%Y-%m-%d %H:%M:%S')} 已过晚上10点，休眠 {sleep_seconds} 秒")
        time.sleep(sleep_seconds)
    else:
        pass

def wait_qcounter(counter):
    sleep_until_next_day_9am()
    '''
    l1_counter, l1_low, l1_high = 1, 15, 120   # 短：快速打开很多；看一个打开一个
    l2_counter, l2_wait         = 25, 300      # 中
    l3_counter, l3_wait         = 500, 8*3600  # 1天
    '''
    l3_counter_low, l3_counter_high, l3_wait         = 300, 500, 3600  # 1天，今天训练结束
    l3_counter = random.randint(l3_counter_low, l3_counter_high)

    l2_counter_low, l2_counter_high, l2_wait         = 55, 75, 300       # 中, 稍微休息
    l2_counter = random.randint(l2_counter_low, l2_counter_high)

    l1_counter, l1_low, l1_high = 1, 10, 45                              # 短：快速打开很多；看一个打开一个

    counter += 1
    if counter % l3_counter == 0:
        wait_time = l3_wait
        now = datetime.now()
        print(f"Reached {l3_counter} Waiting for {wait_time}s {now.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(wait_time)
    if counter % l2_counter == 0:
        wait_time = l2_wait
        print(f"Reached {l2_counter}. Waiting for {wait_time}s")
        time.sleep(wait_time)
    else:
        wait_time = random.randint(l1_low, l1_high)
        print(f"... {wait_time}s")
        time.sleep(wait_time)
    return counter

def getdb_bookid(client, source_ip, username, book_str, book_id):
    session = login(client, username)
    if session is None:
        print("登录失败")
        quit()
        return
    #adapter = SourceIPAdapter(source_ip)
    #session.mount('http://', adapter)
    #session.mount('https://', adapter)

    start_t = time.time()
    code_1_list = []  # 获取页面失败
    code_2_list = []  # fail to find g_qq (maybe not login)
    code_3_list = []  # decode fail, getq 就退出，很严重，json内容找错了
    code_4_list = []  # 不共享
    getq_counter = 0

    db = client[db_name]
    book_q_str = 'book_' + book_str + '_q'
    book_q_collection = db[book_q_str]
    book_collection = db["book_" + book_str]

    # 找到book_id，没成功抓取的url_frombook
    documents = book_q_collection.find({'book_id': book_id, 'status': { '$nin': [0,1,2] }}, {'_id': 0, 'url_no':1, 'url_frombook': 1}).sort('url_frombook', 1)
    #data_list = [doc.get('url_frombook') for doc in documents]
    data_list = [{'url_no': doc.get('url_no'), 'url_frombook': doc.get('url_frombook')} for doc in documents]
    if len(data_list) == 0:
        print(f"No document found with {book_id}")
        result = book_collection.update_one({'id': book_id}, {'$set': {'status': 'ok'}})
        print(f"book_{book_str} id {book_id}: ok {result}")
        return
    print(f'bookid {book_id} {len(data_list)} urls (status!=2) ')

    # 在book库，锁定book_id
    result = book_collection.update_one({'id': book_id}, {'$set': {'status': 'doing'}})
    print(f"book_{book_str} id {book_id}: doing/LOCKED!!! {result}")

    q_collection = db['q']
    cur_no = 0
    new_no = 0
    #for url_frombook in data_list:
    for data_item in data_list:
        url_no = data_item.get('url_no')
        url_frombook = data_item['url_frombook']

        # 提高命中率,假定url_no就是publicid
        if url_no is not None and url_no != '':
            ret = q_collection.find_one({'publicid': int(url_no)})
            if ret:
                #print(f'重复 {url_no}')
                continue

        cur_no += 1
        #print(f'{book_q_str} {book_id} {url_frombook} {cur_no}th')
        print(f'{url_frombook} {url_no} {cur_no}th', end=' ')
        result = getq_url_frombook(client, session, book_q_str, url_frombook)
        inc_getqnum(client, username)

        if result.get('ret') == False:
            code = result.get('code')
            if code == 1: # 页面抓取失败
                code_1_list.append(url_frombook)
            if code == 2: # 找不到 g_qq, 可能没登录
                code_2_list.append(url_frombook)
                if len(code_2_list) >=2:
                    quit()
            if code == 3: # decode g_qq 失败,不会到这儿
                code_3_list.append(url_frombook)
            if code == 4: # not public
                url_from_q = '/q/' + str(url_no) + '/'
                result = getq_url_frombook_from_q(client, session, book_q_str, url_frombook, url_from_q)
                print('retry getq_url_frombook_from_q', result.get('ret'))
        else:
            # 成功时，0不重复，1重复
            if result.get('code') == 0:
                new_no += 1
            print(f'效率：{100*new_no/cur_no:.0f}%', end=' ')
        getq_counter = wait_qcounter(getq_counter)

    # 设置 book_n中，book_id的 status字段为ok，即完成抓取
    result = book_collection.update_one({'id': book_id}, {'$set': {'status': 'ok'}})
    print(f"book_{book_str} id {book_id}: ok {result}")

    end_t = time.time()
    print("获取页面失败（code=1）列表：", code_1_list)
    print("g_qq        （code=2）列表：", code_2_list)
    print("不共享      （code=3）列表：", code_3_list)
    print("不共享      （code=3）列表：", code_4_list)
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

        # 找下一个book_n 中不存在 status字段的book, 即没有抓取过的book
        query = {
            '$or': [
                {'status': {'$exists': False}},
                {'status': {'$nin': ['ok', 'doing']}}
            ]
        }
        documents = book_collection.find(query, {'id': 1, '_id': 0})
        data_list = [doc.get('id') for doc in documents]

def getdb_book_404(source_ip, username, book_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col_404 = db[f'book_{book_str}_q_404']

    docs = book_q_col_404.find({'status': {'$nin':[0,1,2]}},  {'book_id': 1})
    book_404_set = set()
    for doc in docs:
        book_404_set.add(doc.get('book_id'))

    for book_id in book_404_set:
        getdb_bookid(client, source_ip, username, book_str, book_id)

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
        #adapter = SourceIPAdapter(source_ip)
        #session.mount('http://', adapter)
        #session.mount('https://', adapter)

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
        #getdb_book_404(source_ip, username, book_str)
        print('getdb book', username, book_str, 'done')
    else:
        print('getdb_book.py source_ip username book_str book_id url_frombook')
        print('getdb_book.py source_ip username book_str book_id')
        print('getdb_book.py source_ip username book_str: choose idle id to get')
        quit()


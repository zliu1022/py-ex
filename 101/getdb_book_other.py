#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 抓取level, size, question, clone
# 没有book列表
# 不需要登录，不需要延时休息

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

def getdb_bookid(client, username, book_name):
    session = login(client, username)
    if session is None:
        print("登录失败")
        quit()
        return

    start_t = time.time()
    code_1_list = []  # 获取页面失败
    code_2_list = []  # 未登录
    code_3_list = []  # 解析错，很严重，json内容找错了
    code_4_list = []  # 不共享
    code_5_list = []  # 题目删除跳转，或被封杀
    getq_counter = 0

    db = client[db_name]
    book_q_str = book_name
    book_q_collection = db[book_q_str]

    # 找到没成功抓取的url_frombook
    documents = book_q_collection.find({'status': { '$nin': [0,1,2] }, 'url_frombook':{'$exists':True}}, {'_id': 0, 'url_no':1, 'url_frombook': 1}).sort('url_frombook', 1)
    data_list = [{'url_no': doc.get('url_no'), 'url_frombook': doc.get('url_frombook')} for doc in documents]
    if len(data_list) == 0:
        print(f"No document found with {book_name}")
        print(f"id {book_name}: ok")
        return
    print(f'bookid {book_name} {len(data_list)} urls (status!=2) ')

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
        print(f'{url_frombook} {url_no} {cur_no}th', end=' ')
        result = getq_url_frombook(client, session, book_q_str, url_frombook)
        inc_getqnum(client, username)

        if result.get('ret') == False:
            code = result.get('code')
            if code == 1: # 页面抓取失败
                code_1_list.append(url_frombook)
            if code == 2: # 找不到 g_qq, 没登录，立即退出
                code_2_list.append(url_frombook)
            if code == 3: # decode g_qq 失败,不会到这儿
                code_3_list.append(url_frombook)
                quit()
            if code == 4: # not public
                code_4_list.append(url_frombook)
                quit()
                #url_from_q = '/q/' + str(url_no) + '/'
                #result = getq_url_frombook_from_q(client, session, book_q_str, url_frombook, url_from_q)
                #print('retry getq_url_frombook_from_q', result.get('ret'))
            if code == 5: # 题目删除的跳转，或者被封杀（/q/会跳到登录页)
                # 对应status 1000
                code_5_list.append(url_frombook)
                quit()
                #url_from_q = '/q/' + str(url_no) + '/'
                #result = getq_url_frombook_from_q(client, session, book_q_str, url_frombook, url_from_q)
                #print('跳转retry getq_url_frombook_from_q', result.get('ret'))
        else:
            # 成功时，0不重复，1重复
            if result.get('code') == 0:
                new_no += 1
            print(f'效率：{100*new_no/cur_no:.0f}%', end=' ')
        #getq_counter = wait_qcounter(getq_counter)

    print(f"id {book_name}: ok")

    end_t = time.time()
    print("获取页面失败（code=1）列表：", code_1_list)
    print("g_qq        （code=2）列表：", code_2_list)
    print("解码错      （code=3）列表：", code_3_list)
    print("不共享      （code=4）列表：", code_4_list)
    print("跳转，被封杀（code=5）列表：", code_5_list)
    print(f'id {book_name} {cur_no} done')
    print('cost {:5.2f}s'.format(end_t - start_t))
    print('------------------------------------------------------------')

if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    if len(sys.argv) == 3:
        username = sys.argv[1]
        book_name = sys.argv[2]

        getdb_bookid(client, username, book_name)
        print('getdb bookid', username, book_name, 'done')
    else:
        print('getdb_book.py username book_name')
        quit()


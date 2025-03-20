#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from getq import getq

import time
import random

def getdb_doc(documents):
    code_1_list = []  # 获取页面失败
    code_2_list = []  # 登录失败
    code_3_list = []  # 解析json失败

    getq_counter = 0
    cur_no = 0
    for doc in documents:
        url_no = doc.get('url_no')
        level = doc.get('level')
        title_id = doc.get('title_id')
        if title_id:
            continue

        client = MongoClient('mongodb://localhost:27017/')
        db = client['101']
        q_col = db['q']
        docs = q_col.find({'url_no': url_no})
        if docs and len(list(docs)) >1:
            print(f"{url_no} {level} already get {len(list(docs))}")
            continue

        if level is None:
            print(f"{url_no} level is None")
            level = 'q'

        if level[-1] == "+":
            level = level[:-1]
        cur_no += 1
        print(f"{url_no} {level} {cur_no}th")

        result = getq(level, url_no)

        if result.get('ret') == False:
            code = result.get('code')
            if code == 1:
                code_1_list.append(url_no)
            elif code == 2:
                code_2_list.append(url_no)
            elif code == 3:
                code_3_list.append(url_no)

        getq_counter += 1
        if getq_counter == 100:
            print("Reached 50 calls to getq. Waiting for 300 seconds.")
            time.sleep(300)
            getq_counter = 0  # 重置计数器
        else:
            wait_time = random.randint(5, 10)
            print(f"Waiting for {wait_time} seconds.")
            time.sleep(wait_time)
        print()

    print("获取页面失败（code=1）的no列表：")
    print(code_1_list)
    print("登录失败（code=2）的no列表：")
    print(code_2_list)
    print("解析json失败（code=3）的no列表：")
    print(code_3_list)

# 针对 q表中已经有的题目，进行更新
def getdb_q():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['101']
    collection = db['q']
    documents = collection.find()
    if documents:
        getdb_doc(documents)
    else:
        print("No document found in 'q'")

import time
def getdb_level_doc(level_str, documents):
    start_t = time.time()

    client = MongoClient('mongodb://localhost:27017/')
    db = client['101']
    q_collection = db['q']

    code_1_list = []  # 获取页面失败
    code_2_list = []  # 登录失败
    code_3_list = []  # 解析json失败

    getq_counter = 0
    cur_no = 0
    for no in documents:
        ret = q_collection.find_one({'url_no': no})
        if ret:
            print(f'{no} 已经存在')
            continue

        cur_no += 1
        print(f'url_no {no} {cur_no}th', end=' ')
        result = getq(level_str, no)
        if result.get('ret') == False:
            code = result.get('code')
            if code == 1:
                code_1_list.append(no)
            elif code == 2:
                code_2_list.append(no)
            elif code == 3:
                code_3_list.append(no)

        getq_counter += 1
        if getq_counter == 180:
            print("Reached 50 calls to getq. Waiting for 300 seconds.")
            time.sleep(310)
            getq_counter = 0  # 重置计数器
        else:
            #wait_time = random.randint(5, 10), 168个后失败
            #wait_time = random.randint(10, 20), 362个后失败
            wait_time = random.randint(15, 30) #189个后失败
            print(f"Waiting for {wait_time} seconds.")
            time.sleep(wait_time)

    print("获取页面失败（code=1）的no列表：")
    print(code_1_list)
    print("登录失败（code=2）的no列表：")
    print(code_2_list)
    print("解析json失败（code=3）的no列表：")
    print(code_3_list)

    end_t = time.time()
    print(f'{cur_no} done')
    print('cost {:5.2f}s'.format(end_t - start_t))

# 针对 level表中的列表，进行获取
def getdb_level(level_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['101']
    level_collection = db['level']

    document = level_collection.find_one({'level': level_str})

    if document:
        list_array = document.get('list', [])
        getdb_level_doc(level_str, list_array)
    else:
        print(f"No document found with level {level_str}")

if __name__ == "__main__":
    #getdb_q()
    getdb_level('2K')

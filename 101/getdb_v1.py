#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from getq_v1 import getq
import time
import random
import sys

def getdb_level_doc(client, username, level_str, documents):
    start_t = time.time()

    db = client['101']
    q_collection = db['q']

    code_1_list = []  # 获取页面失败
    code_2_list = []  # 登录失败
    code_3_list = []  # 解析json失败

    getq_counter = 0
    cur_no = 0
    for no in documents:
        #ret = q_collection.find_one({'url_no': no})
        ret = q_collection.find_one({
            'url_no': no,
            'status': {'$ne': 404}
        })
        if ret:
            print(f'{no} 已经存在')
            continue

        cur_no += 1
        print(f'url_no {no} {cur_no}th', end=' ')
        result = getq(client, username, level_str, no)
        if result.get('ret') == False:
            code = result.get('code')
            if code == 1:
                code_1_list.append(no)
            elif code == 2:
                code_2_list.append(no)
            elif code == 3:
                code_3_list.append(no)

        getq_counter += 1
        if getq_counter == 125:
            # 189th: 189 x 21.5/22.5 = 180
            # 130th: 130 x 21.5/22.5 = 125
            wait_time = 300
            print(f"Reached 125 calls to getq. Waiting for {wait_time} seconds")
            time.sleep(wait_time)
            getq_counter = 0  # 重置计数器
        else:
            wait_time = random.randint(15, 30) #189th失败,130th失败
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
def getdb_level(username, level_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['101']
    level_collection = db['level']
    document = level_collection.find_one({'level': level_str})

    if document:
        list_array = document.get('list', [])
        getdb_level_doc(client, username, level_str, list_array)
    else:
        print(f"No document found with level {level_str}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        username = sys.argv[1]
        level_str = sys.argv[2]
    else:
        quit()
    getdb_level(username, level_str)
    print(username, level_str, 'done')


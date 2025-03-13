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

    for doc in documents:
        no = doc.get('no')
        print(f"No. {no}")
        result = getq(no)

        if result.get('ret') == False:
            code = result.get('code')
            if code == 1:
                code_1_list.append(no)
            elif code == 2:
                code_2_list.append(no)
            elif code == 3:
                code_3_list.append(no)
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

def getdb_level_doc(documents):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['101']
    q_collection = db['q']

    code_1_list = []  # 获取页面失败
    code_2_list = []  # 登录失败
    code_3_list = []  # 解析json失败

    for doc in documents:
        print(f"No. {doc}")

        ret = q_collection.find_one({'no': doc})
        if ret:
            print('已经存在')
            continue

        result = getq(doc)
        if result.get('ret') == False:
            code = result.get('code')
            if code == 1:
                code_1_list.append(doc)
            elif code == 2:
                code_2_list.append(doc)
            elif code == 3:
                code_3_list.append(doc)
        print()
        wait_t = random.randint(10, 20)
        time.sleep(wait_t)

    print("获取页面失败（code=1）的no列表：")
    print(code_1_list)
    print("登录失败（code=2）的no列表：")
    print(code_2_list)
    print("解析json失败（code=3）的no列表：")
    print(code_3_list)

# 针对 level表中的列表，进行获取
def getdb_level(level_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['101']
    level_collection = db['level']

    document = level_collection.find_one({'level': level_str})

    if document:
        list_array = document.get('list', [])
        getdb_level_doc(list_array)
    else:
        print("No document found with level '9K'")

if __name__ == "__main__":
    #getdb_q()
    getdb_level('9K')

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
mongodb, db_name库，q集合
找没有 title_id字段的文档
获得该文档的 url_no字段内容
查找全部文档
如果相同 url_no且有 title_id字段的文档个数超过 1个，则记录有几个这样的文档，输出个数
如果相同 url_no的文档，都是没有 title_id字段，输出这样文档的个数，以及 url_no
'''

from pymongo import MongoClient
from config import db_name

# 连接 MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client[db_name]  # 选择数据库
q_collection = db["q"]  # 选择集合

empty_title_list = []
strange_title_list = []
docs_list = list(q_collection.find({"title_id": {"$exists": False}}))
for doc in docs_list:
    url_no = doc['url_no']
    ret = list(q_collection.find({"url_no": url_no}))
    if len(ret) == 1:
        empty_title_list.append(url_no)
    elif len(ret) > 2:
        strange_title_list.append({'url_no':url_no, 'strange_num':len(ret)})

# 输出
print(f'empty titile_id: {len(empty_title_list)}')
print(f'strange titile_id: {len(strange_title_list)}')
print(strange_title_list)


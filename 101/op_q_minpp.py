#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 为了能够实时搜索棋形，得到匹配的数量
# 增加能配合 $all搜索的字段,放入表格 q_search

import json
from pymongo import MongoClient
from config import db_name

client = MongoClient()
db = client[db_name]
collection = db['q']
col_s = db['q_search']

# 为每个文档添加 min_pp_list 字段
for doc in collection.find({}):
    min_pp_string = doc.get('min_pp', '[]')

    if isinstance(min_pp_string, list):
        print(f" _id={doc['_id']} {min_pp_string} {doc.get('url_no')} {doc.get('title_id')}")
        continue

    try:
        min_pp_array = json.loads(min_pp_string)  # 解析为 Python 列表
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON in document _id={doc['_id']} {min_pp_string} {e}")
        continue  # 跳过此文档，处理下一个

    # 将每个棋子表示为字符串，如 "b-1-3"
    try:
        min_pp_list = [f"{entry[0]}-{entry[1]}-{entry[2]}" for entry in min_pp_array]
    except (IndexError, TypeError) as e:
        print(f"Error processing entry in document _id={doc['_id']} {min_pp_string} {e}")
        continue

    # 更新文档，添加 min_pp_list 字段
    col_s.update_one({'min_pp': min_pp_string}, {'$set':{'min_pp_list': min_pp_list}}, upsert=True)

# 在 min_pp_list 字段上创建索引
col_s.create_index('min_pp_list')


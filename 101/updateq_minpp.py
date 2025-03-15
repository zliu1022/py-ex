#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import json
from matchq_v3 import canonicalize_positions

# 连接到 MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['101']
collection = db['q']

# 获取集合中的索引信息
indexes = collection.index_information()

# 检查并删除 'no' 字段上的唯一索引
if 'no_1' in indexes:
    if indexes['no_1'].get('unique', False):
        print("正在删除 'no' 字段上的唯一索引...")
        collection.drop_index('no_1')

# 将 'no' 字段重命名为 'url_no'
print("正在将 'no' 字段重命名为 'url_no'...")
collection.update_many({}, {'$rename': {'no': 'url_no'}})

# 处理每个文档，计算并添加 'min_pp' 字段
print("正在处理文档以添加 'min_pp' 字段...")
cursor = collection.find({}, no_cursor_timeout=True)

for doc in cursor:
    doc_id = doc['_id']
    prepos = doc.get('prepos')
    if prepos is None:
        print(f"文档 _id {doc_id} 缺少 'prepos' 字段，特殊处理。")
        stones_key_list = [['_invalid_', str(doc_id)]]
        stones_key_json = json.dumps(stones_key_list, sort_keys=True)
        collection.update_one({'_id': doc_id}, {'$set': {'min_pp': stones_key_json}})
        continue

    # 调用 match.py 中的函数计算 stones_key
    stones_key = canonicalize_positions(prepos)
    # 将 stones_key（元组的元组）转换为列表的列表
    stones_key_list = [list(item) for item in stones_key]
    # 将 stones_key_list 序列化为 JSON 字符串
    stones_key_json = json.dumps(stones_key_list, sort_keys=True)
    # 更新文档，添加 'min_pp' 字段
    collection.update_one({'_id': doc_id}, {'$set': {'min_pp': stones_key_json}})

# 创建 'min_pp' 字段上的唯一索引
print("正在为 'min_pp' 字段创建唯一索引...")
collection.create_index('min_pp', unique=True)

print("更新完成。")

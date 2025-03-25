#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
集合：4，5，6，7，8，9，11，13，chizi，guanzi，buju，zhongpan，qili，shizhan, pianzhao, shizhan
集合里的文档格式如下：
{
  "url_level": "15K+",
  "url_no": "218455"
}
对于这些集合中的每个文档，编程python，检查下是否与另外一个 grade集合中的信息重复，统计有多少重复，有多少不重复
'''

from pymongo import MongoClient
from config import db_name

# 连接 MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client[db_name]

# 要处理的集合
collections_to_check = ['11', '13', '4', '5', '6', '7', '8', '9', 'buju', 'chizi', 'guanzi', 'pianzhao', 'qili', 'shizhan', 'zhongpan']

# grade 集合
grade_collection = db['grade']

# 统计
total_docs = 0
duplicate_count = 0
non_duplicate_count = 0

for collection_name in collections_to_check:
    collection = db[collection_name]

    print(f"正在检查集合：{collection_name}")

    for doc in collection.find({}, {'url_level': 1, 'url_no': 1}):
        total_docs += 1

        url_level = doc.get('url_level')
        url_no = doc.get('url_no')

        if not url_level or not url_no:
            # 缺少关键字段，算不重复
            non_duplicate_count += 1
            continue

        # 在 grade 集合查找是否存在
        match = grade_collection.find_one({
            'level_str': url_level,
            'url_no': url_no
        })

        if match:
            duplicate_count += 1
        else:
            non_duplicate_count += 1

print("===== 统计结果 =====")
print(f"总文档数: {total_docs}")
print(f"重复的文档数: {duplicate_count}")
print(f"不重复的文档数: {non_duplicate_count}")

client.close()


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
建立新集合 grade
对于 level集合，每一个文档，把内部的list数组，重新建立成一个数组元素一个文档的机构
{
    "level_str": 就是 文档的level,
    "url_no": 就是 文档的list数组中的一个元素
}
'''

from pymongo import MongoClient

# 连接 MongoDB
client = MongoClient("mongodb://localhost:27017/")  # 根据实际情况修改连接信息
db = client["101"]  # 选择数据库
level_collection = db["level"]  # 选择原集合
grade_collection = db["grade"]  # 目标集合

# 清空 grade 集合（可选）
#grade_collection.delete_many({})

# 遍历 level 集合，将数据转换格式
documents = level_collection.find()
new_docs = []

for doc in documents:
    level_str = doc["level"]
    for url_no in doc["list"]:
        new_docs.append({"level_str": level_str, "url_no": url_no})

    # 分批插入，避免单次插入过大
    if len(new_docs) > 1000:
        grade_collection.insert_many(new_docs)
        new_docs = []

# 插入剩余数据
if new_docs:
    grade_collection.insert_many(new_docs)

print("转换完成！")


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
grade 集合，结构：
{
    "level_str": "9K",
    "url_no": "4958"
}
怎么查询其中是否存在 重复数据，即level_str和url_no都相等的文档
'''

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["101"]
grade_collection = db["grade"]

# 聚合查询，统计重复的 (level_str, url_no)
pipeline = [
    {
        "$group": {
            "_id": {"level_str": "$level_str", "url_no": "$url_no"},
            "count": {"$sum": 1}
        }
    },
    {"$match": {"count": {"$gt": 1}}}  # 过滤出 count > 1 的，即重复的
]

duplicates = list(grade_collection.aggregate(pipeline))

# 输出重复数据
if duplicates:
    print("存在重复数据：")
    for doc in duplicates:
        print(doc["_id"], "重复次数:", doc["count"])
else:
    print("没有重复数据")


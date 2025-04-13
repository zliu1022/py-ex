#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import db_name

# count_qtype_status_2: 统计 status:2的情况下，各种不同的 qtype各有多少个文档
# count_level_status_2_sorted: 统计 status:2的情况下，各种不同的 level各有多少个文档，

level_total = {
    "15K":4752, 
    "14K":5116, 
    "13K":4701, 
    "12K":4700, 
    "11K":4676, 
    "10K":7037,
    "9K":6922, 
    "8K":7115, 
    "7K":8679, 
    "6K":8862, 
    "5K":9514, 
    "4K":9503, 
    "3K":9260, 
    "2K":10021, 
    "1K":8401,
    "1D":7371, 
    "2D":7240, 
    "3D":7413, 
    "4D":8118, 
    "5D":8891, 
    "6D":8134, 
    "7D":691
}

def count_qtype_status_2():
    client = MongoClient()  # 默认连接 localhost
    db = client[db_name]
    collection = db['q']

    pipeline = [
        {"$match": {"status": 2}},
        {"$group": {"_id": "$qtype", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}  # 可选：按数量降序排序
    ]

    results = collection.aggregate(pipeline)

    for r in results:
        print(f"qtype: {r['_id']}, count: {r['count']}")
        break

def count_leveltype_status_2():
    client = MongoClient()  # 默认连接 localhost
    db = client[db_name]
    collection = db['q']

    pipeline = [
        {"$match": {"status": 2}},
        {"$group": {"_id": "$level", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}  # 可选：按数量降序排序
    ]

    results = collection.aggregate(pipeline)

    for r in results:
        print(f"level: {r['_id']}, count: {r['count']}")
        break

def count_level_status_2_sorted():
    client = MongoClient()
    db = client[db_name]
    collection = db['q']

    # 自定义排序顺序
    level_order = [
        "15K", "14K", "13K", "12K", "11K", "10K",
        "9K", "8K", "7K", "6K", "5K", "4K", "3K", "2K", "1K",
        "1D", "2D", "3D", "4D", "5D", "6D", "7D"
    ]

    print(f"| level | count | 死活题 | 总数   | 完成率 |")
    print(f"| ----- | ----- | ------ | ------ | ------ |")
    # 根据排序顺序输出
    total_ok = 0
    total_ok_deadlive = 0
    total = 0
    for level in level_order:
        ret = collection.find({"status": 2, "level":{"$regex": f"^{level}"}})
        all_data_list = [doc.get('_id') for doc in ret]
        count = len(all_data_list)

        ret = collection.find({"status": 2, "qtype":"死活题", "level":{"$regex": f"^{level}"}})
        data_list = [doc.get('_id') for doc in ret]
        perc = 100*float(count)/float(level_total.get(level))
        print(f"| {level:>5} | {count:>5} | {len(data_list):>6} | {level_total.get(level):>6} | {perc:>5.0f}% |") 

        total_ok += count
        total_ok_deadlive += len(data_list)
        total += level_total.get(level)

    perc = 100*float(total_ok)/float(total)
    print(f"| total | {total_ok} | {total_ok_deadlive:>6} | {total:>6} | {perc:>5.0f}% |") 

if __name__ == "__main__":
    print("status == 2, 各种qtype的题目数量")
    count_qtype_status_2()
    print("status == 2, 各种level的题目数量")
    count_leveltype_status_2()
    print("status == 2, level规范后的题目总数、死活题数量")
    count_level_status_2_sorted()


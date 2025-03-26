#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import db_name

# count_qtype_status_2: 统计 status:2的情况下，各种不同的 qtype各有多少个文档
# count_level_status_2_sorted: 统计 status:2的情况下，各种不同的 level各有多少个文档，

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


def count_level_status_2_sorted():
    client = MongoClient()
    db = client[db_name]
    collection = db['q']

    pipeline = [
        {"$match": {"status": 2, "qtype":"死活题"}},
        {"$group": {"_id": "$level", "count": {"$sum": 1}}}
    ]

    results = list(collection.aggregate(pipeline))

    # 自定义排序顺序
    level_order = [
        "15K", "14K", "13K", "12K", "11K", "10K",
        "9K", "8K", "7K", "6K", "5K", "4K", "3K", "2K", "1K",
        "1D", "2D", "3D", "4D", "5D", "6D", "7D"
    ]

    # 将结果转为字典方便查找
    result_dict = {r['_id']: r['count'] for r in results}

    print(f"| level | count | 死活题 | 总数 |")
    print(f"| --- | --- | --- | --- |")
    # 根据排序顺序输出
    for level in level_order:
        count = result_dict.get(level, 0)

        ret = collection.find({"status": 2, "qtype":"死活题", "status":2, "level":level})
        data_list = [doc.get('_id') for doc in ret]
        print(f"| {level} | {count} | {len(data_list)} |  |")


if __name__ == "__main__":
    print("qtype 统计")
    count_qtype_status_2()

    print("\nlevel 统计")
    count_level_status_2_sorted()


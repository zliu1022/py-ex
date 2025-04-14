#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 统计各种status的文档个数

from pymongo import MongoClient
from config import db_name
import sys

def stat_book_q_status(book_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    collection = db['book_' + book_str + '_q']

    pipeline = [
        {
            '$group': {
                '_id': '$status',
                'count': { '$sum': 1 }
            }
        }
    ]

    results = collection.aggregate(pipeline)

    for result in results:
        if result['_id'] == 2 or result['_id'] is None:
            print(f"Status=={result['_id']} {result['count']}")

def statdb_book_running_status(book_str):
    # 连接到MongoDB
    client = MongoClient()
    db = client[db_name]
    book_5 = db['book_'+book_str]
    book_5_q = db['book_' + book_str + '_q']

    # 查询book_5集合中有status字段的文档
    cursor = book_5.find({"status": {"$exists": True}}, {"id": 1, "status": 1, "_id": 0})

    print("| book_id | status | total | status==2 | other |")
    print("| ------- | ------ | ----- | --------- | ----- |")
    for doc in cursor:
        book_id = doc.get('id')
        status = doc.get('status')

        # 在book_5_q集合中查询book_id等于id的文档，并统计各种status的数量
        pipeline = [
            {"$match": {"book_id": book_id}},
            {"$group": {"_id": "$status", "count": {"$sum": 1}}},
        ]

        counts = list(book_5_q.aggregate(pipeline))

        total = sum([c['count'] for c in counts])

        status_2_count = 0
        other_status_counts = {}
        for c in counts:
            status_value = c['_id']
            count = c['count']
            if status_value == 2:
                status_2_count = count
            else:
                other_status_counts[status_value] = count

        '''
        !!! 慎重
        if total - status_2_count >= 5:
            result = book_5.update_one({"id": book_id}, {"$unset": {"status": ""}})
        elif total == status_2_count:
            if status != 'ok':
                result = book_5.update_one({"id": book_id}, {"$set": {"status": "ok"}})
        '''

        if status == "ok" and total == status_2_count:
            continue
            
        # 打印结果
        print(f"| {book_id:>7} | {status:>6} | {total:>5} | {status_2_count:>9} | ", end='')
        for k, v in other_status_counts.items():
            print(f"status: {k} {v} |", end=' ')
        print()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        book_str = sys.argv[1]
        statdb_book_running_status(book_str)
        stat_book_q_status(book_str)
    else:
        quit()

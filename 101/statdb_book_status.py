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

    print('全部book中')
    for result in results:
        if result['_id'] == 2 or result['_id'] is None:
            print(f"Status=={result['_id']} {result['count']}")

def statdb_book_running_status(book_str):
    # 连接到MongoDB
    client = MongoClient()
    db = client[db_name]
    book_5 = db['book_'+book_str]
    book_5_q = db['book_' + book_str + '_q']

    # 统计book总数，已经抓取过的book
    count_all = book_5.count_documents({})
    count_ok = book_5.count_documents({"status": {"$exists": True}})
    print(f'总共 {count_all} 本书，已抓取 {count_ok} 本书')

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

        #if status == "ok": # 跳过这些：下载过一遍，跳过q中已有publicid
        if status == "ok" and total == status_2_count: # 跳过这些：全部下载过一遍
            continue
            
        # 打印结果
        print(f"| {book_id:>7} | {status:>6} | {total:>5} | {status_2_count:>9} | ", end='')
        for k, v in other_status_counts.items():
            print(f"status: {k} {v} |", end=' ')
        print()

def statdb_all():
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    book_total = 0
    book_total_ok = 0
    q_total = 0
    q_total_ok = 0
    print("| level | book_ok |  total  |   ok%  |   q_ok  |  total  |   ok%  |  doing  |   ok   | total |")
    print("| ----- | ------- | ------- | ------ | ------- | ------- | ------ | ------- | ------ | ----- |")
    for n in range(1, 6):
        collection_name = f'book_{n}'
        collection = db[collection_name]
        total_docs = collection.count_documents({})
        ok_docs = collection.count_documents({'status': 'ok'})
        doing_doc = collection.find_one({'status': 'doing'})
        if total_docs > 0:
            proportion = ok_docs / total_docs * 100
        else:
            proportion = 0
        print(f'| {n:>5} | {ok_docs:>7} | {total_docs:>7} | {proportion:>5.1f}% |', end=' ')
        book_total += total_docs
        book_total_ok += ok_docs

        collection_name = f'book_{n}_q'
        collection = db[collection_name]
        total_docs = collection.count_documents({})
        status2_docs = collection.count_documents({'status': 2})
        if total_docs > 0:
            proportion = status2_docs / total_docs * 100
        else:
            proportion = 0
        print(f'{status2_docs:>7} | {total_docs:>7} | {proportion:>5.1f}% |', end=' ')
        q_total += total_docs
        q_total_ok += status2_docs

        if doing_doc is not None: 
            doing_total = collection.count_documents({'book_id': doing_doc['id']})
            doing_ok = collection.count_documents({'book_id': doing_doc['id'], 'status': 2})
            print(f'{doing_doc['id']:>7} | {doing_ok:>6} | {doing_total:>5} |')
        else:
            print()

    print(f'| total | {book_total_ok:>7} | {book_total:>7} | {book_total_ok/book_total*100:>5.1f}% | {q_total_ok:>7} | {q_total:>7} | {q_total_ok/q_total*100:>5.1f}% |')

if __name__ == "__main__":
    if len(sys.argv) == 2:
        book_str = sys.argv[1]
        statdb_book_running_status(book_str)
        stat_book_q_status(book_str)
        quit()
    else:
        statdb_all()

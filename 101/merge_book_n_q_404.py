#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient, UpdateOne
from pymongo.errors import BulkWriteError

import sys
from config import db_name, base_url

def comp(book_str):
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    book_q_col = db[f'book_{book_str}_q']
    book_q_col_404 = db[f'book_{book_str}_q_404']

    s1 = []
    s2 = []
    s3 = []
    s4 = []
    s5 = []
    for doc_404 in book_q_col_404.find().sort('book_id', 1):
        book_id = doc_404['book_id']
        url_no = doc_404['url_no']

        # Check for a conflicting document in book_n_q with the same book_id and url_no
        query = {'book_id': book_id, 'url_no': url_no}
        doc_q = book_q_col.find_one(query)

        if doc_q:
            # url_frombook中含有/0/：替换
            # url_frombook相同: 跳过
            # 只是url_no相同：跳过
            if doc_q['url_frombook'].find('/0/') != -1:
                # book_q_col.update_one(doc_404)
                print(f"existing /0/ {book_id} {url_no}: ", end=' ')
                print(f"{doc_404['url_frombook']} {doc_404.get('status')}", end=' ')
                print(f"{doc_q['url_frombook']} {doc_q.get('status')}")
            elif doc_q['url_frombook'] == doc_404['url_frombook']:
                if doc_q.get('status') == doc_404.get('status'):
                    continue
                else:
                    print(f"existing same url {book_id} {url_no}: ", end=' ')
                    print(f"{doc_404['url_frombook']} {doc_404.get('status')}", end=' ')
                    print(f"{doc_q['url_frombook']} {doc_q.get('status')}")
            else:
                print(f"existing only url_no same {book_id} {url_no}: ", end=' ')
                print(f"{doc_404['url_frombook']} {doc_404.get('status')}", end=' ')
                print(f"{doc_q['url_frombook']} {doc_q.get('status')}")
                continue
        else:
            print(f"new {book_id} {url_no}: {doc_404.get('status')}")
            # book_q_col.insert_one(doc_404)

def merge(book_n):
    # 连接到MongoDB数据库
    client = MongoClient('localhost', 27017)
    db = client[db_name]  # 请将'your_database'替换为您的实际数据库名称

    # 获取集合
    book_1_q = db[f'book_{book_n}_q']
    book_1_q_404 = db[f'book_{book_n}_q_404']

    # 第一步：在'url_frombook'和'book_id'字段上创建唯一索引
    print("正在为'url_frombook'和'book_id'字段创建唯一索引...")
    # 首先，删除已有的索引（如果存在）
    existing_indexes = book_1_q.index_information()
    index_name = 'url_no_1_book_id_1'
    if index_name in existing_indexes:
        book_1_q.drop_index(index_name)
        print(f"已删除book_1_q中已有的索引 {index_name}。")

    # 第二步：对于book_1_q_404集合中的每一个book_id，执行指定操作
    print("正在处理book_1_q_404中的book_id...")
    book_ids = book_1_q_404.distinct('book_id')
    print(f"在book_1_q_404中找到{len(book_ids)}个唯一的book_id。")

    for book_id in book_ids:
        print(f"正在处理book_id: {book_id}")

        # 第二步a：删除book_1_q中book_id相同的文档
        delete_result = book_1_q.delete_many({'book_id': book_id})
        print(f"已从book_1_q中删除book_id为{book_id}的{delete_result.deleted_count}个文档。")

    # 创建新的唯一复合索引
    book_1_q.create_index(
        [('url_frombook', 1), ('url_no', 1), ('book_id', 1)],
        unique=True,
        name=index_name
    )
    print("唯一复合索引创建完成。")

    for book_id in book_ids:
        print(f"正在处理book_id: {book_id}")

        # 第二步b：将book_1_q_404中book_id相同的文档复制到book_1_q
        docs_to_move = list(book_1_q_404.find({'book_id': book_id}))

        # 删除'_id'以避免插入时的主键冲突
        for doc in docs_to_move:
            if '_id' in doc:
                del doc['_id']

        if docs_to_move:
            try:
                # 将文档插入book_1_q集合
                insert_result = book_1_q.insert_many(docs_to_move, ordered=False)
                print(f"已将{len(insert_result.inserted_ids)}个文档插入book_1_q，book_id为{book_id}。")
            except BulkWriteError as bwe:
                # 处理重复键错误
                write_errors = bwe.details.get('writeErrors', [])
                for error in write_errors:
                    if error.get('code') == 11000:
                        # 重复的文档，不用处理
                        print(f"发现重复的文档，已跳过。错误详情：{error['errmsg']}")
                    else:
                        print("发生其他错误：", error['errmsg'])
        else:
            print(f"book_id为{book_id}的文档不存在需要移动。")

    quit()

    for book_id in book_ids:
        print(f"正在处理book_id: {book_id}")

        # 第二步c：删除book_1_q_404中book_id相同的文档
        delete_result_404 = book_1_q_404.delete_many({'book_id': book_id})
        print(f"已从book_1_q_404中删除book_id为{book_id}的{delete_result_404.deleted_count}个文档。")

if __name__ == "__main__":
    if len(sys.argv) == 2:
        book_str = sys.argv[1]
        #comp(book_str)
        merge(book_str)


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 为了能够实时搜索棋形，得到匹配的数量
# 增加能配合 $all搜索的字段,放入表格 q_search
'''
30000docs read 0.66s insert 0.38s total 0.65s 30000/197672
30000docs read 0.62s insert 0.21s total 0.48s 60000/197672
30000docs read 0.49s insert 0.20s total 0.57s 90000/197672
30000docs read 0.50s insert 0.20s total 0.59s 120000/197672
30000docs read 0.45s insert 0.23s total 0.52s 150000/197672
30000docs read 0.54s insert 0.36s total 0.62s 180000/197672
17672docs read 0.12s insert 0.15s total 0.31s 197672/197672
All documents processed.
Index on 'min_pp_list' created in 2.99s
Total processing time: 10.11s
'''

from config import db_name

import json
import logging
import time
from pymongo import MongoClient, UpdateOne

# 数据库连接
client = MongoClient('mongodb://localhost:27017/')
db = client[db_name]  # 请替换为您的数据库名称
collection = db['q']
col_search = db['q_search']

batch_size = 30000  # 每批处理的文档数量
cursor = collection.find({})
total_docs = collection.count_documents({})
processed_docs = 0

total_start_time = time.time()
while True:
    # 开始计时 - 读取操作
    read_start_time = time.time()

    # 从游标中批量获取文档
    batch = []
    try:
        for _ in range(batch_size):
            doc = next(cursor)
            batch.append(doc)
    except StopIteration:
        # 已经遍历完所有文档
        if not batch:
            break

    # 结束计时 - 读取操作
    read_end_time = time.time()
    read_time = read_end_time - read_start_time
    print(f"{len(batch)}docs read {read_time:.2f}s", end=' ')

    # 开始计时 - 处理和写入操作
    process_write_start_time = time.time()

    new_documents = []  # 用于存储新创建的文档
    for doc in batch:
        min_pp_data = doc.get('min_pp', [])

        # 检查 min_pp_data 的类型
        if isinstance(min_pp_data, str):
            # 如果是字符串，尝试解析为列表
            try:
                min_pp_array = json.loads(min_pp_data)
            except json.JSONDecodeError as e:
                error_message = f"Error decoding JSON in document _id={doc['_id']}: {e}"
                print(error_message)
                logging.error(error_message)
                continue  # 跳过此文档，处理下一个
        else:
            print(f"min_pp field is neither str nor list in document _id={doc['_id']}: type={type(min_pp_data)}")
            continue

        # 将每个棋子表示为字符串，如 "b-1-3"
        min_pp_list = []
        for entry in min_pp_array:
            try:
                min_pp_list.append(f"{entry[0]}-{entry[1]}-{entry[2]}")
            except (IndexError, TypeError) as e:
                print(f"Error processing entry in document _id={doc['_id']}: entry={entry}, error={e}")
                continue  # 跳过此 entry，继续处理下一个

        # 创建新的文档
        new_doc = {
            'min_pp': min_pp_data,
            'min_pp_list': min_pp_list
        }
        new_documents.append(new_doc)

    # 批量插入新文档
    if new_documents:
        insert_start_time = time.time()
        col_search.insert_many(new_documents)
        insert_end_time = time.time()
        insert_time = insert_end_time - insert_start_time

        processed_docs += len(new_documents)
        process_write_end_time = time.time()
        process_write_time = process_write_end_time - process_write_start_time
        print(f"insert {insert_time:.2f}s total {process_write_time:.2f}s", end=' ')
        print(f"{processed_docs}/{total_docs}")
    else:
        process_write_end_time = time.time()
        process_write_time = process_write_end_time - process_write_start_time
        print(f"No documents to insert in this batch. Processing time: {process_write_time:.2f} seconds.")

print("All documents processed.")

# 更新完成后，创建索引
index_start_time = time.time()
col_search.create_index('min_pp_list')
index_end_time = time.time()
index_time = index_end_time - index_start_time
print(f"Index on 'min_pp_list' created in {index_time:.2f}s")

total_end_time = time.time()
total_time = total_end_time - total_start_time
print(f"Total processing time: {total_time:.2f}s")


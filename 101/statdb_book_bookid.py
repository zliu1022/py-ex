#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import re
import numpy as np
import matplotlib.pyplot as plt
import math
from config import db_name

#函数1, 每个集合统计 唯一的 book_id 数量, 所有集合合并后统计 唯一的 book_id 数量
#函数2 针对每个集合，对每个 book_id： 统计它所有 url_frombook 末尾数字的 最小值和最大值

def comp_unique_book_ids():
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    all_book = set()
    print(f'| n | book_ids(book_n) | book_id(book_n_q) | exception |')
    for n in range(1,6):
        book_n_col = db[f'book_{n}']
        book_n_q_col = db[f'book_{n}_q']

        b = set(book_n_col.distinct('id'))
        bq = set(book_n_q_col.distinct('book_id'))
        no_set = b-bq

        print(f'| {n:>1} | {len(b):>16} | {len(bq):>18} | {len(no_set):>9} |')
        #draw_distribution(b)

        if len(no_set) != 0: 
            print(no_set)
        all_book.update(b)
    draw_distribution(all_book)

def draw_distribution(all_book):
    # Convert the set to a sorted list for easier handling (optional)
    publicid_list = sorted(all_book)

    # Find the minimum and maximum values
    min_value = min(publicid_list)
    max_value = max(publicid_list)

    print(f"Minimum value: {min_value}")
    print(f"Maximum value: {max_value}")

    unit_size = 4000
    # Create bins of size 
    # The bins will start from min_value and go up to max_value
    # We add an extra 1000 to include the max_value in the last bin
    int_max_value = int(max_value/unit_size)*unit_size
    bin_edges = np.arange(1, int_max_value + 2*unit_size, unit_size)

    # Count the number of publicid values in each bin
    counts, bins = np.histogram(publicid_list, bins=bin_edges)

    # Print the counts per bin
    print("Count of id in each range bin:")
    for i in range(len(counts)):
        print(f"Range {int(bins[i])} to {int(bins[i+1])}: {counts[i]}")

    # Plot the distribution using a histogram
    plt.figure(figsize=(10, 6))
    plt.hist(publicid_list, bins=bin_edges, edgecolor='black', alpha=0.7)
    plt.xlabel('ID Range')
    plt.ylabel('Frequency')
    plt.title(f'Distribution of IDs (Bin Size = {unit_size})')
    plt.xticks(bin_edges, rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

def draw_missing_distribution(all_book):
    publicid_list = sorted([int(item) for item in all_book if item != ""])

    # 4. 找出最小的和最大的 publicid
    min_id = publicid_list[0]
    max_id = publicid_list[-1]
    print(f'publicid range {min_id} {max_id}')

    # 5. 找出缺失的 publicid
    publicid_set = set(publicid_list)  # 转为 set 以提高查询效率
    missing_ids = []
    for pid in range(min_id, max_id + 1):
        if pid not in publicid_set:
            missing_ids.append(pid)

    # 6. 打印结果
    if missing_ids:
        print(f"缺失的 publicid 有 {len(missing_ids)} 个")
        #print(missing_ids)
    else:
        print("publicid 连续无缺失。")

    # 计算总的分段数量
    segment_size = 2000
    total_segments = math.ceil((max_id - min_id + 1) / segment_size)

    # 初始化结果列表
    missing_counts = []

    # 逐个分段统计缺失的 publicid 数量
    for i in range(total_segments):
        segment_start = min_id + i * segment_size
        segment_end = min(segment_start + segment_size - 1, max_id)
        segment_ids = set(range(segment_start, segment_end + 1))
        missing_ids = segment_ids - publicid_set
        missing_count = len(missing_ids)
        missing_counts.append(missing_count)
        if i<20:
            print(f"区间 {segment_start}-{segment_end}: 缺失 {missing_count} 个 publicid")

    # 绘制结果
    segment_labels = [f"{min_id + i * segment_size}-{min(min_id + (i + 1) * segment_size - 1, max_id)}" for i in range(total_segments)]
    x = range(total_segments)
    y = missing_counts

    plt.figure(figsize=(12, 6))

    #plt.plot(x, y, marker='o')
    plt.bar(x, y)

    plt.xticks(x, segment_labels, rotation=45)
    plt.xlabel('PublicID range')
    plt.ylabel('missing PublicID counts')
    plt.title('missing PublicID counts / 1000 range')
    plt.grid(False)
    plt.tight_layout()
    plt.show()

def comp_unique_book_ids_url_no():
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    publicid_set = set(db['q'].distinct('publicid'))

    print(f'book_n | book_id | unique_url_no | not_in_q |')
    for n in range(1,6):
        book_n_col = db[f'book_{n}']
        book_n_q_col = db[f'book_{n}_q']

        books = book_n_col.find({}, {'id': 1}).sort('id', 1)
        total = 0
        for b in books:
            book_id = b.get('id')

            #status = book_n_col.find_one({'id':book_id}).get('status')
            #if status == 'doing':
            #    continue

            # 每一本book，没有获取过的url_no, 且不在q库 publicid集合中
            #ret = book_n_q_col.distinct('url_no', filter={'book_id': book_id, 'status':{'$exists':False}})
            ret = book_n_q_col.distinct('url_no', filter={'book_id': book_id, 'status':{'$nin':[0,1,2]}})

            url_nos = set([int(item) for item in ret if item != ""])
            url_no_nin_pubid = url_nos - publicid_set

            if len(url_no_nin_pubid) != 0:
                print(f'book_{n} {book_id} {len(url_nos)} {len(url_no_nin_pubid)} ...{url_no_nin_pubid}')

                book_n_col.update_one({"id": book_id}, {"$unset": {"status": ""}})

                total += 1
                continue
        print(f'book_{n} total', total)

def main():
    #comp_unique_book_ids()
    comp_unique_book_ids_url_no()

if __name__ == "__main__":
    main()

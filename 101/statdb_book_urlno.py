#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import db_name
import pymongo
import matplotlib.pyplot as plt
import math

# 统计每个book_n中，有多少没有抓取过的url_no (即没有status字段）
# 这些url_no，作为publicid，有多少还没有被抓取过

def statdb_book_publicid():
    # 1. 连接 MongoDB（根据实际情况修改主机、端口或认证）
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[db_name] # 选择数据库

    publicid_set = set(db['q'].distinct('publicid'))
    print('统计没有抓取过的url_no，都有对应publicid')
    print('publicid_set', len(publicid_set))

    url_no_set = set()
    for n in range(1,6):
        collection = db[f"book_{n}_q"] # 选择集合

        url_nos = collection.distinct('url_no', filter={'status':{'$exists':False}})
        url_no_list = [int(item) for item in url_nos if item != ""]
        url_no_set_n = set(url_no_list)
        url_no_set_no_not_get = url_no_set_n - publicid_set
        print(f'book_{n} unique_url_no {len(url_no_set_n)} not_in_q {len(url_no_set_no_not_get)}')

        url_no_set.update(url_no_set_n)

    url_no_not_get = url_no_set - publicid_set
    print(f'all book unique_url_no {len(url_no_set)} not_in_q {len(url_no_not_get)}')
    quit()
    publicid_list = sorted([int(item) for item in url_no_set if item != ""])

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
    segment_size = 10000
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

if __name__ == "__main__":
    statdb_book_publicid()

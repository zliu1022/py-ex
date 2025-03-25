#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import pandas as pd
from config import db_name

#函数1：输入单个集合，按照顺序['15K', '14K', '13K', '12K', '11K', '10K', '9K', '8K', '7K', '6K', '5K', '4K', '3K', '2K', '1K', '1D', '2D', '3D', '4D', '5D', '6D', '7D']，
#统计里面 url_level不同类别的数量
#函数2：统计5个集合，每个集合中  url_level不同类别的数量，打印成表格，每一列是一个集合，每一行是一种 url_level类别
#每个url_level的求和，每个book_n_q的求和

level_order = [
    "15K", "14K", "13K", "12K", "11K", "10K",
    "9K", "8K", "7K", "6K", "5K", "4K", "3K", "2K", "1K",
    "1D", "2D", "3D", "4D", "5D", "6D", "7D"
]

def statdb_onebook_levelcount(book_str):
    client = MongoClient()
    db = client[db_name]
    collection = db[book_str]

    pipeline = [
        {"$group": {"_id": "$url_level", "count": {"$sum": 1}}}
    ]

    results = list(collection.aggregate(pipeline))

    count_dict = {level: 0 for level in level_order}

    for item in results:
        level = item['_id']
        if level in count_dict:
            count_dict[level] = item['count']

    return count_dict


if __name__ == "__main__":
    print("\nlevel 统计")
    book_list = ['book_1_q', 'book_2_q', 'book_3_q', 'book_4_q', 'book_5_q']
    all_levelcount = {}
    for book_str in book_list:
        ret = statdb_onebook_levelcount(book_str)
        all_levelcount[book_str] = ret

    print("| level | book_1_q | book_2_q | book_3_q | book_4_q | book_5_q | 求和 |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    sumcount = {}
    for l in level_order:
        print('|', l, end=' | ')
        count = 0
        for b in book_list:
            count += all_levelcount[b][l]
            if sumcount.get(b):
                sumcount[b] += all_levelcount[b][l]
            else:
                sumcount[b] = all_levelcount[b][l]
            print(all_levelcount[b][l], end=' | ')
        print(count)

    print('| ', '求和', end=' | ')
    for b in book_list:
        print(sumcount[b], end=' | ')
    print()


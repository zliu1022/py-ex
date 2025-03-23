#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
import re

#函数1, 每个集合统计 唯一的 book_id 数量, 所有集合合并后统计 唯一的 book_id 数量
#函数2 针对每个集合，对每个 book_id： 统计它所有 url_frombook 末尾数字的 最小值和最大值

# 连接MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['101']

# 集合名列表
collections = ['book_1_q', 'book_2_q', 'book_3_q', 'book_4_q', 'book_5_q']

def count_unique_book_ids():
    """
    统计每个集合中唯一 book_id 数量，及全部集合唯一 book_id 数量
    """
    all_book_ids = set()

    for col_name in collections:
        col = db[col_name]
        book_ids = col.distinct('book_id')
        all_book_ids.update(book_ids)
        print(f'集合 {col_name} 中唯一 book_id 数量: {len(book_ids)}')

    print(f'\n所有集合中唯一 book_id 总数: {len(all_book_ids)}')

def find_min_max_url_numbers():
    """
    统计每个集合中，每个 book_id 的 url_frombook 最小值和最大值
    """
    # 正则匹配 url_frombook 结尾数字
    pattern = re.compile(r'/(\d+)/?$')

    for col_name in collections:
        col = db[col_name]
        pipeline = [
            {
                '$group': {
                    '_id': '$book_id',
                    'url_list': {'$push': '$url_frombook'}
                }
            }
        ]

        results = col.aggregate(pipeline)
        print(f'\n集合 {col_name}:')

        for result in results:
            book_id = result['_id']
            url_list = result['url_list']
            numbers = []

            for url in url_list:
                match = pattern.search(url)
                if match:
                    numbers.append(int(match.group(1)))

            if numbers:
                min_num = min(numbers)
                max_num = max(numbers)
                print(f'  book_id {book_id} -> 最小值: {min_num}, 最大值: {max_num}')
            else:
                print(f'  book_id {book_id} -> 无有效的 url_frombook')

# 执行函数
count_unique_book_ids()
find_min_max_url_numbers()


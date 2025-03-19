#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient

# 统计每个 book_n_q中唯一的 url_no个数
# 统计所有 book_n_q中唯一的 url_no个数,返回
def stat_unique_urlno():
    client = MongoClient("mongodb://localhost:27017/")
    db = client['101']

    book_collections = ['book_1_q', 'book_2_q', 'book_3_q', 'book_4_q', 'book_5_q']

    unique_url_nos = set()

    for col_name in book_collections:
        collection = db[col_name]

        # Obtain distinct 'url_no's in the current collection
        url_nos = collection.distinct('url_no')
        print(f"{col_name} {len(url_nos)} unique 'url_no'")

        unique_url_nos.update(url_nos)

    print(f"all book {len(unique_url_nos)} unique 'url_no'")
    print()

    client.close()
    return list(unique_url_nos)

# 比对所有book_n_q中的唯一url_no和grade中的唯一url_no
def stat_book_grade_unique(unique_url_nos):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['101']
    grade_collection = db['grade']

    grade_url_nos = set(grade_collection.distinct('url_no'))
    print(f"grade unique 'url_no' {len(grade_url_nos)}")

    # Find 'url_no's that are in both sets
    url_nos_in_grade = unique_url_nos.intersection(grade_url_nos)
    # Find 'url_no's that are only in the book collections
    url_nos_not_in_grade = unique_url_nos.difference(grade_url_nos)

    print(f"'url_no' in book_n_q and grade: {len(url_nos_in_grade)}")
    print(f"'url_no' in book_n_q NOT in 'grade': {len(url_nos_not_in_grade)}")

    client.close()
    return {
        'count_in_grade': len(url_nos_in_grade),
        'count_not_in_grade': len(url_nos_not_in_grade),
        'url_nos_in_grade': list(url_nos_in_grade),
        'url_nos_not_in_grade': list(url_nos_not_in_grade)
    }

if __name__ == "__main__":
    # Function 1: Get unique 'url_no's from book collections
    unique_url_nos = set(stat_unique_urlno())

    # Function 2: Compare with 'grade' collection
    result = stat_book_grade_unique(unique_url_nos)

    # If you want to use the results further, you can access the result dictionary
    # For example, to get the list of 'url_no's not in 'grade' collection:
    urls_not_in_grade = result['url_nos_not_in_grade']

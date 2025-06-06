#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 就是把表格 15K，9K 的文档，全部移动到 level表格中
# 移动前先进行 level里面list数组的比较, 一个level有一个list数组

from pymongo import MongoClient
from config import db_name, base_url

# 先把原来的level和新的15k，14k等表格进行比对，然后插入
def check_level():
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    levels_collection = db['level']
    for doc in levels_collection.find():
        level = doc['level']
        list_elements = doc['list']

        # Access the collection corresponding to the 'level' field
        level_collection = db[level]

        for element in list_elements:
            existing_doc = level_collection.find_one({'url_no': element})

            if not existing_doc:
                new_doc = { 'url_no': element, 'url_frombook': f"/{level}/{element}/", 'url_level': level }
                level_collection.insert_one(new_doc)
                print(f"new '{level}': {new_doc}")

# 然后手动清空level表格数据

# 把15K，14K等表格数据移动到level库
# 要移动的集合列表
def move_level():
    collections_to_move = [
        '15K', '14K', '13K', '12K', '11K', '10K',
        '9K', '8K', '7K', '6K', '5K', '4K', '3K',
        '2K', '1K', '1D', '2D', '3D', '4D', '5D',
        '6D', '7D'
    ]

    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    for col_name in collections_to_move:
        collection = db[col_name]
        docs = list(collection.find())
        if docs:
            db['level'].insert_many(docs)
        collection.drop()  # 删除原集合

    # 输出对应的 mongosh 命令
    collection_list_string = '[' + ', '.join(f"'{col}'" for col in collections_to_move) + ']'
    print("var collections = {};\n".format(collection_list_string))
    print("collections.forEach(function(colName) {")
    print("   db.getCollection(colName).aggregate([")
    print("       { $match: {} },")
    print("       { $merge: { into: 'level' } }")
    print("   ]);")
    print("   db.getCollection(colName).drop();")
    print("});")

if __name__ == "__main__":
    move_level()

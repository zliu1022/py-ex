#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 就是把表格 13，11, 9等 的文档，全部移动到 size表格中

from pymongo import MongoClient
from config import db_name, base_url

def move_size():
    collections_to_move = [
        '13', '11', '9', '8', '7', '6', '5', '4'
    ]

    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    for col_name in collections_to_move:
        collection = db[col_name]
        docs = list(collection.find())
        if docs:
            db['size'].insert_many(docs)
        collection.drop()  # 删除原集合

    # 输出对应的 mongosh 命令
    collection_list_string = '[' + ', '.join(f"'{col}'" for col in collections_to_move) + ']'
    print("var collections = {};\n".format(collection_list_string))
    print("collections.forEach(function(colName) {")
    print("   db.getCollection(colName).aggregate([")
    print("       { $match: {} },")
    print("       { $merge: { into: 'size' } }")
    print("   ]);")
    print("   db.getCollection(colName).drop();")
    print("});")

if __name__ == "__main__":
    move_size()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import db_name, base_url

# 连接到 MongoDB 数据库
client = MongoClient('mongodb://localhost:27017/')
db = client[db_name]        # 替换为您的数据库名称
collection = db['book_4_q_404']  # 替换为您的集合名称

# 使用聚合管道将 book_id 字段从字符串转换为整数
collection.update_many(
    {},
    [
        {
            "$set": {
                "book_id": {
                    "$toInt": "$book_id"
                }
            }
        }
    ]
)

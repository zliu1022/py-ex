#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from pymongo import MongoClient, ReturnDocument
import sys
from pprint import pprint

from config import site_name, base_url, cache_dir, db_name

def getbook_onelevel(content):
    # 提取var books变量的数据
    start_marker = 'var books = ['
    end_marker = '];'

    start_index = content.find(start_marker)
    if start_index != -1:
        end_index = content.find(end_marker, start_index)
        if end_index != -1:
            # 提取books_data
            books_data = content[start_index + len('var books = '): end_index + 1]  # 包含最后的'}'
            try:
                # 解析JSON数据
                books = json.loads(books_data)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                return {'ret': False, 'code': 1, 'message':'JSON解析错误'}
            return {'ret': True, 'data': books}
        else:
            return {'ret': False, 'code': 2, 'message':'未找到结束标记'}
    else:
        return {'ret': False, 'code': 3, 'message':'未找到起始标记'}

# same as getq
def dict_diff(old, new, path=''):
    differences = {}
    # 收集所有的键，包括新旧字典中特有的键
    keys = set(new.keys()).union(set(old.keys()))
    for key in keys:
        old_value = old.get(key)
        new_value = new.get(key)
        current_path = f"{path}.{key}" if path else key
        if isinstance(old_value, dict) and isinstance(new_value, dict):
            # 递归比较子字典
            sub_differences = dict_diff(old_value, new_value, path=current_path)
            if sub_differences:
                differences.update(sub_differences)
        elif old_value != new_value:
            differences[current_path] = {'old': old_value, 'new': new_value}
    return differences


from pprint import pprint
def getbooklist(booklist_html, book_level):
    # MongoDB连接设置
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client[db_name]
    collection = db["book_"+str(book_level)]

    # 为集合创建唯一索引
    collection.create_index('id', unique=True)

    with open(booklist_html, 'r', encoding='utf-8') as f:
        content = f.read()

    ret = decode_book(content)
    if ret == False:
        return

    for doc in ret.get('data'):
        '''
        {
            'username': '方块A', 
            'name': '真珠诘棋', 
            'userpos': 96, 
            'booktype': 0, 
            'is_disabled': False, 
            'tags': [{'id': 50, 'name': '山田晋次'}], 
            'userid': 9316, 
            'desctext': '山田晋次六段监修（注：由于题目简单，内有大量题目和古典死活还有名家名作重复）', 
            'is_share': True, 
            'score': 450, 
            'chapters': [], 
            'pinyin': '', 
            'id': 27534, 
            'ba': {'qcount': 55, 'qlevelname': '6K+'}
        }

        book_name = book.get('name', '')
        book_id = book.get('id', '')
        book_url = f"/book/{book_id}/" if book_id else ''
        ba = book.get('ba', '')
        book_qnum = ba.get('qcount', '')
        book_level = ba.get('qlevelname', '')
        book_comment = book.get('desctext', '')
        #print(f"{book_name} {book_url} {book_qnum} {book_level} {book_comment[0:10]}")
        '''

        col_filter = {'id': doc['id']}
        old = collection.find_one_and_replace(
            filter=col_filter,
            replacement=doc,
            upsert=True,
            return_document=ReturnDocument.BEFORE  # 返回更新前的文档
        )
        if old:
            old.pop('_id', None)

            differences = dict_diff(old, doc)
            if differences:
                print("以下字段已被更新：")
                for field, change in differences.items():
                    print(f"{field}: 从 {change['old']} 更新为 {change['new']}")
            else:
                print("数据已存在，且无任何变化。")
        else:
            print(f"集合book_{book_level} 插入新文档 {doc['id']} {doc['name']}")

def getdb_book_onelevel(client, book_n, booklist_html):
    db = client[db_name]
    col = db["book_"+str(book_n)]

    with open(booklist_html, 'r', encoding='utf-8') as f:
        content = f.read()

    ret = getbook_onelevel(content)
    if ret.get('ret') == False:
        print(f'getbook_onelevel {book_n} {booklist_html} fail')
        quit()

    for doc in ret.get('data'):
        book_id = doc['id']
        ret = col.find_one({'id': book_id})

        # book_id已经存在，就进行比较
        if ret is not None:
            continue

            # 去除不需要比较的字段
            ret.pop('_id', None)
            ret.pop('status', None)
            ret.pop('cover', None)
            ret.pop('comment', None)

            # 去除修正过的字段
            ret.pop('chapters', None)
            doc.pop('chapters', None)

            ret.pop('ba', None)
            doc.pop('ba', None)

            differences = dict_diff(ret, doc)
            if differences:
                print(f'book_id {book_id}')
                print("以下字段已被更新：")
                for field, change in differences.items():
                    print(f"{field}: 从 {change['old']} 更新为 {change['new']}")
            else:
                continue
                print("数据已存在，且无任何变化。")
            continue

        print(f'missing book_{book_n} {book_id}')

        col_filter = {'id': doc['id']}
        old = col.find_one_and_replace(
            filter=col_filter,
            replacement=doc,
            upsert=True,
            return_document=ReturnDocument.BEFORE  # 返回更新前的文档
        )
        if old:
            old.pop('_id', None)

            differences = dict_diff(old, doc)
            if differences:
                print("以下字段已被更新：")
                for field, change in differences.items():
                    print(f"{field}: 从 {change['old']} 更新为 {change['new']}")
            else:
                print("数据已存在，且无任何变化。")
        else:
            print(f"集合book_{book_n} 插入新文档 {doc['id']} {doc['name']}")

def getdb_book_level(n):
    books = [
        {'file':"book_1.html", 'level':1, 'url': '/book/level/1/'},
        {'file':"book_2.html", 'level':2, 'url': '/book/level/2/'},
        {'file':"book_3.html", 'level':3, 'url': '/book/level/3/'},
        {'file':"book_4.html", 'level':4, 'url': '/book/level/4/'},
        {'file':"book_5.html", 'level':5, 'url': '/book/level/5/'},
    ]
    client = MongoClient('mongodb://localhost:27017/')
    for b in books:
        booklist_html = b['file']
        book_n = b['level']
        if book_n == n:
            getdb_book_onelevel(client, book_n, booklist_html)

if __name__ == "__main__":
    if len(sys.argv) == 3:
        book_n = sys.argv[1]
        file_name = sys.argv[2]
        with open(file_name, 'r', encoding='utf-8') as f:
            content = f.read()
        ret = getbook_onelevel(content)
        if ret.get('ret'):
            for doc in ret.get('data'):
                print(doc)
                quit()
    elif len(sys.argv) == 2:
        book_n = int(sys.argv[1])
        getdb_book_level(book_n)
    elif len(sys.argv) == 1:
        getdb_book_level()
    else:
        quit()

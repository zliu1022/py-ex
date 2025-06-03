#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import db_name
from pymongo import MongoClient
from getq_fromq import getq_fromq 
from getq_v1 import login

book_ex_list = [
    {'id': 41653, 'name': '围棋练习册 入门篇（上）', 'nodecount': 0},
    {'id': 41654, 'name': '围棋练习册 入门篇（中）', 'nodecount': 0},
    {'id': 41655, 'name': '围棋练习册 入门篇（下）', 'nodecount': 0},
    {'id': 42156, 'name': '围棋练习册 初级篇（上）', 'nodecount': 0},
    {'id': 42163, 'name': '围棋练习册 初级篇（中）', 'nodecount': 0},
    {'id': 42175, 'name': '围棋练习册 初级篇（下）', 'nodecount': 0},
    {'id': 42907, 'name': '围棋练习册 中级篇（上）', 'nodecount': 0},
    {'id': 42908, 'name': '围棋练习册 中级篇（中）', 'nodecount': 0},
    {'id': 42909, 'name': '围棋练习册 中级篇（下）', 'nodecount': 0},
    {'id': 42920, 'name': '围棋练习册 高级篇（上）', 'nodecount': 0},
    {'id': 42921, 'name': '围棋练习册 高级篇（中）', 'nodecount': 0},
    {'id': 42922, 'name': '围棋练习册 高级篇（下）', 'nodecount': 0},
    {'id': 42983, 'name': '专项练习册-从15K到14K', 'nodecount': 659},
    {'id': 42984, 'name': '专项练习册-从13K到12K', 'nodecount': 600},
    {'id': 42985, 'name': '专项练习册-从11K到10K', 'nodecount': 689},
    {'id': 42986, 'name': '专项练习册-从9K到8K', 'nodecount': 599},
    {'id': 42987, 'name': '专项练习册-从7K到6K', 'nodecount': 600},
    {'id': 42988, 'name': '专项练习册-从5K到4K', 'nodecount': 680},
    {'id': 42989, 'name': '专项练习册-从3K到2K', 'nodecount': 560},
    {'id': 42990, 'name': '专项练习册-从1K到1D', 'nodecount': 659},
    {'id': 42991, 'name': '专项练习册-从2D到3D', 'nodecount': 650},
    {'id': 42992, 'name': '专项练习册-从4D到5D', 'nodecount': 800}
 ]

def browse_book_ex_id(book_id):
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    book_ex_col = db['book_ex']
    book_ex_q_col = db['book_ex_q']

    doc = book_ex_col.find_one({'id': book_id})
    print(f'{doc.get('name')} {doc.get('id')}')
    for ch in doc.get('chapters'):
        print(f'    {ch['name']} {ch['nodecount']} {len(ch['subs'])}')
        for subch in ch.get('subs'):
            subch_id = subch.get('id')
            print(f'        {subch['name']} {subch['desc']} {subch['nodecount']}')

            docs = book_ex_q_col.find({'book_id':book_id, 'url_frombook':{'$regex':f'/book/{book_id}/{subch_id}/'}})
            for doc in docs:
                url_no = int(doc['url_no'])
                print(f'            {url_no} {doc['url_level']} {doc['url_frombook']} ->', end=' ')
                ret = find_url_no_all_q(url_no)
                if ret.get('ret'):
                    print(f'{ret.get('data')}')
                else:
                    print(f'没找到')

def browse_book_ex():
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    book_ex_col = db['book_ex']

    for b in book_ex_list:
        book_id = b.get('id')
        book_name = b.get('name')
        browse_book_ex_id(book_id)

def find_url_no_all_q(url_no):
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    book_ex_q_col = db['book_ex_q']

    found = False

    for n in range(0, 6):
        if n == 0:
            collection_name = f'q'
        else:
            collection_name = f'book_{n}_q'
        collection = db[collection_name]

        result = collection.find_one({'publicid': url_no})
        if result:
            found = True
            if n == 0: #在q中找到
                #print(f'找到 {book_id} {url_no} -> q')
                return {'ret': True, 'data': {'n':'q', 'st':result.get('status')}, 'code': 0}
            else: #在book_n中找到
                url_frombook = result.get('url_frombook')
                if result.get('min_pp'):
                    result = db['q'].find_one({'min_pp': result.get('min_pp')})
                    if result:
                        return {'ret': True, 'data': {'name':'q', 'status':result.get('status'), 'id':result.get('publicid')}, 'code': 0}
                return {'ret': True, 'data': {'name':f'book_{n}', 'status':result.get('status')}, 'code': 0}
            break

    if not found:
        #print(f'没找到 {book_id} {url_no}')
        return {'ret': False, 'code': 1}

# 统计 book_ex_q中还有多少需要抓取的题目
# 即，没有status的题目，不能匹配publicid
def stat_book_ex_status():
    client = MongoClient('localhost', 27017)
    db = client[db_name]
    book_ex_q_col = db['book_ex_q']

    for ex_doc in book_ex_q_col.find({'status':{'$exists':False}}).sort('book_id', 1):
        url_no = int(ex_doc.get('url_no'))
        book_id = ex_doc.get('book_id')
        found = False

        # Check in 'book_n_q' collections where n ranges from 1 to 5
        for n in range(0, 6):
            if n == 0:
                collection_name = f'q'
            else:
                collection_name = f'book_{n}_q'
            collection = db[collection_name]

            # Try querying with 'publicid' as a string
            result = collection.find_one({'publicid': url_no})
            if result:
                found = True
                if n == 0:
                    #print(f'找到 {book_id} {url_no} -> q')
                    pass
                else:
                    url_frombook = result.get('url_frombook')
                    #print(f'找到 {book_id} {url_no} -> book_{n} {url_frombook}')
                break

        if not found:
            print(f'没找到 {book_id} {url_no}')
            #getq_fromq(client, session, url_no)

if __name__ == "__main__":
    stat_book_ex_status()
    #browse_book_ex()

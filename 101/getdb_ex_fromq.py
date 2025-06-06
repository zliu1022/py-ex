#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 针对book_ex 的url_no，检查q，book_n 里的publicid
# 找不到的只能通过 /q/访问，要慎重

from pymongo import MongoClient, ReturnDocument
from getq_v1 import login, getq_url_frombook, inc_getqnum, getq_url_frombook_from_q, get_url_v1, resp_json_url_frombook_v2, update_q_v1
import time
import random
import sys
from config import db_name, base_url
from datetime import datetime, timedelta
from ip import SourceIPAdapter
import time
from pprint import pprint

from getq_fromq import getq_fromq
from getdb_book import wait_qcounter

book_ex_id_list = [
  41653, 41654, 41655, 42156,
  42163, 42175, 42907, 42908,
  42909, 42920, 42921, 42922,
  42983, 42984, 42985, 42986,
  42987, 42988, 42989, 42990,
  42991, 42992
]
def getdb_ex_onebook(client, session, book_id):
    db = client[db_name]
    book_ex_q_col = db['book_ex_q']

    getq_counter = 0
    count = 0
    for ex_doc in book_ex_q_col.find({'book_id': book_id}).sort('url_no', 1):
        book_id      = ex_doc.get('book_id')
        url_no       = ex_doc.get('url_no')
        url_frombook = ex_doc.get('url_frombook')
        #if int(url_no) <= 266030:
        #    continue

        result = []
        for n in range(0, 6):
            if n == 0:
                collection_name = f'q'
            else:
                collection_name = f'book_{n}_q'
            collection = db[collection_name]

            docs = collection.find({'publicid': int(url_no)})
            for doc in docs:
                result.append({
                    'id':           doc.get('_id'),
                    'book_n':       n,
                    'status':       doc.get('status'),
                    'url_no':       doc.get('url_no'),
                    'url_frombook': doc.get('url_frombook')
                })
            docs = collection.find({'url_no': str(url_no)})
            for doc in docs:
                result.append({
                    'id':           doc.get('_id'),
                    'book_n':       n,
                    'status':       doc.get('status'),
                    'url_no':       doc.get('url_no'),
                    'url_frombook': doc.get('url_frombook')
                })

        if result:
            found = False
            for r in result:
                if r.get('status') == 2:
                    found = True
                    break
            if found == True:
                print(f"找到 {book_id} {url_no} {url_frombook} ->", r) 
                pass
            else:
                print(f'找到 {book_id} {url_no} {url_frombook} 但是status != 2', result)
                if count>=5:
                    quit()
                count+=1
        else:
            print(f'没找到 {book_id} {url_no}, 只能直接访问 q')
            ret = getq_fromq(client, session, url_no)
            if ret is not None:
                result = book_ex_q_col.update_one(
                    {'url_frombook': url_frombook},
                    {'$set': {
                        'publicid': ret.get('publicid'), 
                        'min_pp':   ret.get('min_pp'), 
                        'status':   ret.get('status')
                    }}
                )
            getq_counter = wait_qcounter(getq_counter)

if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    if len(sys.argv) == 3:
        username = sys.argv[1]
        session = login(client, username)
        if session is None:
            print("登录失败")
            quit()
        book_id = int(sys.argv[2])
        getdb_ex_onebook(client, session, book_id)
    else:
        print(book_ex_id_list)


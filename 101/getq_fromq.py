#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient, ReturnDocument
from getq_v1 import login, getq_url_frombook, inc_getqnum, getq_url_frombook_from_q, get_url_v1, resp_json_url_frombook_v2, update_q_v1
import time
import random
import sys
from config import db_name, base_url
from datetime import datetime, timedelta
from ip import SourceIPAdapter
import time

# q 的唯一索引是 min_pp
def getq_from_url_no(client):
    db = client[db_name]
    col_q = db['q']

    publicid_set = set(col_q.distinct('publicid'))
    print('q库，唯一publicid：', len(publicid_set))
    url_no_set = set(col_q.distinct('url_no'))
    print('q库，唯一url_no：', len(url_no_set))

    url_no_list = []
    url_no_set = set()
    docs = col_q.find({'publicid': {'$exists': False}},  {'url_no':1, 'min_pp':1})
    for doc in docs:
        '''
        print(f'url_no {doc.get('url_no'):>6}', end=' ')
        ret = col_q.find_one({'publicid': int(doc.get('url_no'))})
        if ret:
            print(f'pubid {ret.get('publicid'):>6}', end=' ')
        else:
            print(f'pubid None  ', end=' ')
        print('bk_n', end=' ')
        for n in range(1,6):
            ret = db[f'book_{n}_q'].find({'min_pp': doc.get('min_pp')})
            for item in ret:
                print(f'{n} {item.get('publicid'):>6} {item.get('url_frombook')}', end=' ')
        print()
        '''
        url_no_list.append(int(doc.get('url_no')))
        url_no_set.add(int(doc.get('url_no')))

    print('q库，没有publicid的全部url_no：', len(url_no_list))
    print('q库，没有publicid的唯一url_no：', len(url_no_set))

    url_no_missing = url_no_set - publicid_set
    print('q库，没有publicid的唯一url_no，且不存在publicid的：', len(url_no_missing))

    quit()

    for url_no in url_no_missing:
        getq_fromq(client, session, url_no)

def getq_fromq(client, session, q_no):
    url = base_url + '/q/' + str(q_no)

    response = get_url_v1(session, url)
    if response.status_code == 200:
        ret = resp_json_url_frombook_v2(client, response.text, url)
        if ret.get('ret'):
            retcode = update_q_v1(client, ret.get('data')) # 0:新增,1:更新
            return ret.get('data')
        else:
            print(f"resp_json fail {url} {ret.get('code')}")
            return None
    else:
        print(f"获取页面失败，{url}")
        return None

def getall_no_answer(client, session):
    db = client[db_name]
    col_q = db['q']
    docs = col_q.find({'status': 2, 'answers':{'$size':0}, 'options':{'$size':0}, 'qtype':'模仿题'},  {'publicid':1, 'qtype':1}).sort('publicid', 1)

    for doc in docs:
        publicid = doc.get('publicid')
        if publicid < 49021: continue
        print(publicid, doc.get('qtype'))
        getq_fromq(client, session, publicid)
        time.sleep(30)

if __name__ == "__main__":
    client = MongoClient('mongodb://localhost:27017/')
    if len(sys.argv) == 3:
        username = sys.argv[1]
        session = login(client, username)
        if session is None:
            print("登录失败")
            quit()
        q_no = sys.argv[2]
        getq_fromq(client, session, q_no)
    elif len(sys.argv) == 2:
        username = sys.argv[1]
        session = login(client, username)
        if session is None:
            print("登录失败")
            quit()
        getall_no_answer(client, session)
    else:
        quit()


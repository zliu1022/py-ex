#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import db_name
from pymongo import MongoClient

# 每个book_n中，有publicid（即被抓取过）的文档有多少个，unique的publicid有多少个

def stat_books_publicid():
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    col = db['q']
    q_pubid_set = set(col.distinct('publicid'))

    book_pubid_set = set()
    total = 0
    for n in range(1,6):
        col = db[f'book_{n}_q']
        pubid_cnt = col.count_documents({"publicid": {'$exists':True}})
        total += pubid_cnt
        uni_pubid_set = set(col.distinct('publicid'))
        print(f'book_{n}_q {pubid_cnt} {len(uni_pubid_set)}')

        book_pubid_set.update(uni_pubid_set)

    print(f'book_n_q {total} {len(q_pubid_set)}')
    print(f'q库中唯一publicid            {len(q_pubid_set)}')
    diff_set = book_pubid_set - q_pubid_set
    print(f'差异 {len(diff_set)}')

def stat_books_from_url_no(collection_name, url_no_not_in_q):
    # 统计不在q中的url_no，对应有多少本books
    unique_books = set()
    #print(url_no_not_in_q)
    for url_no in url_no_not_in_q:
        docs = db[collection_name].find({'url_no': str(url_no)})
        for doc in docs:
            book_id = doc.get('book_id')
            unique_books.add(int(book_id))
    return unique_books

def stat_url_no(url_no_values):
    status_set = set()
    url_no_int_set = set()
    for doc in url_no_values:
        url_no = doc.get('url_no')
        status = doc.get('status')
        if status is not None:
            status_set.add(status)
        if url_no is not None and url_no != '':
            try:
                url_no_int = int(url_no)
                url_no_int_set.add(url_no_int)
            except ValueError:
                # Handle non-integer url_no values here
                print(f"Non-integer url_no found: '{url_no}' in collection {collection_name}")
                continue
        else:
            # Handle None or empty string url_no values
            #print(f"Missing or empty url_no found in collection {collection_name}")
            continue
    return url_no_int_set, status_set

def analyze_collection(n):
    collection_name = f'book_{n}_q'

    # Get unique url_no values
    url_no_values = db[collection_name].find({}, {'url_no': 1, 'status': 1})                              # 所有url_no
    url_no_all, st_set1 = stat_url_no(url_no_values) # 返回unique的url_no和status

    url_no_values = db[collection_name].find({'status':{'$exists': True}, 'status':{'$nin': [0,1,2] }}, {'url_no': 1})         # status不等于2的url_no, 包括获取过但失败的
    url_no_st_not2, st_set2 = stat_url_no(url_no_values)

    url_no_values = db[collection_name].find({'status': { '$exists': False }}, {'url_no': 1}) # 从没获取过的url_no
    url_no_st_none, st_set3 = stat_url_no(url_no_values)

    url_no_values = db[collection_name].find({'status':404}, {'url_no': 1})
    url_no_st_404, st_set4 = stat_url_no(url_no_values)
    url_no_values = db[collection_name].find({'status':404, 'url_frombook':{'$regex':'/0/'}}, {'url_no': 1})
    url_no_st_404_url0, st_set4 = stat_url_no(url_no_values)

    # url_no not in publicid_set
    url_no_all_not_in_q = url_no_all - publicid_set
    url_no_st_not2_not_in_q = url_no_st_not2 - publicid_set
    url_no_st_none_not_in_q = url_no_st_none - publicid_set

    # status 非0，1，2, 从未抓取过，且url_no不在publicid中的book
    total_books_st_not2_not_in_set = stat_books_from_url_no(collection_name, url_no_st_not2_not_in_q)
    book_ids = db[collection_name+'_404'].distinct('book_id')
    book_not_in_404 = total_books_st_not2_not_in_set - set(book_ids)
    if len(book_not_in_404) != 0:
        print(book_not_in_404)
        #for book_id in book_not_in_404:
        #    result = db[f'book_{n}'].update_one({"id": book_id}, {"$unset": {"status": ""}})

    # status 404 的book
    total_books_st_404_not_in_set = set()
    docs = db[collection_name].find({'status':404}, {'book_id': 1})
    for doc in docs:
        total_books_st_404_not_in_set.add(doc.get('book_id'))

    # status 404 而且url_frombook中有"/0/"的book
    total_books_st_404_url0_not_in_set = set()
    docs = db[collection_name].find({'status':404, 'url_frombook':{'$regex':'/0/'}}, {'book_id': 1})
    for doc in docs:
        total_books_st_404_url0_not_in_set.add(doc.get('book_id'))

    # status none, 从未抓取过，且url_no不在publicid中的book
    total_books_st_none_not_in_set = stat_books_from_url_no(collection_name, url_no_st_none_not_in_q)

    # Results
    counts_url_no_all = len(url_no_all)
    counts_url_no_all_not_in_q = len(url_no_all_not_in_q)
    counts_url_no_st_not2 = len(url_no_st_not2)
    counts_url_no_st_not2_not_in_q = len(url_no_st_not2_not_in_q)
    counts_url_no_st_none = len(url_no_st_none)
    counts_url_no_st_none_not_in_q = len(url_no_st_none_not_in_q)

    total_books_st_not2_not_in = len(total_books_st_not2_not_in_set)
    total_books_st_none_not_in = len(total_books_st_none_not_in_set)

    return counts_url_no_all, counts_url_no_all_not_in_q, counts_url_no_st_not2, counts_url_no_st_not2_not_in_q, total_books_st_not2_not_in, counts_url_no_st_none, counts_url_no_st_none_not_in_q, total_books_st_none_not_in

# Function 2: Combined collections analysis
def analyze_all_collections():
    url_no_int_set = set()
    unique_books = set()
    for n in range(1, 6):
        collection_name = f'book_{n}_q'
        url_no_values = db[collection_name].find({}, {'url_no': 1})
        #url_no_values = db[collection_name].find({ 'status': { '$ne': 2 }  }, {'url_no': 1})
        #url_no_values = db[collection_name].find({'status': { '$exists': False }}, {'url_no': 1}) # 从没获取过的url_no
        for doc in url_no_values:
            url_no = doc.get('url_no')
            if url_no is not None and url_no != '':
                try:
                    url_no_int = int(url_no)
                    url_no_int_set.add(url_no_int)
                except ValueError:
                    print(f"Non-integer url_no found: '{url_no}' in collection {collection_name}")
                    continue
            else:
                #print(f"Missing or empty url_no found in collection {collection_name}")
                continue

    url_no_not_in_q = url_no_int_set - publicid_set
    total_unique_url_no = len(url_no_int_set)
    url_no_not_in_q_count = len(url_no_not_in_q)

    return total_unique_url_no, url_no_not_in_q_count


def main():
    # Connect to MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    # Get publicid set from q collection, handling missing and non-integer values
    publicid_set = set()
    for doc in db.q.find({}, {'publicid': 1}):
        publicid = doc.get('publicid')
        if publicid is not None and publicid != '':
            try:
                publicid_int = int(publicid)
                publicid_set.add(publicid_int)
            except ValueError:
                # Handle non-integer publicid values here
                print(f"Non-integer publicid found: '{publicid}'")
                continue
        else:
            # Handle None or empty string publicid values
            #print(f"Missing or empty publicid found")
            continue

    # Function 1: Per collection analysis
    print('url_no_st_not2: 已经抓取过，状态不是0,1,2，可能网络错误，不共享。。。')
    print('url_no_st_none: 从未抓取过')
    print('NOT in q:       不在q的publicid中，而且 1个url_no，可能多条记录，对应多本book')
    print('status:         {0, 1, 2, 404, 500, 504, 520, 522, 524, 525, 600, 700, 900}')
    print('700: qq fail; 800: decode fail; 900: not public')
    '''
    print('0审核，1淘汰，2入库')
    print('404-525:        网络错误')
    print('600: Connection aborted. RemoteDisconnected Remote end closed connection without response'
                'HTTPSConnectionPool host=xxx, port=443 Read timed out. read timeout=120'
                'Connection aborted. ConnectionResetError 54 Connection reset by peer')
    '''
    print()

    print(f'| book_n_q | url_no | NOT in q | url_no_st_not2 | NOT in q | books | url_no_st_none | NOT in q | books |')
    print(f'| -------- | ------ | -------- | -------------- | -------- | ----- | -------------- | -------- | ----- |')
    for n in range(1, 6):
        collection_name = f'book_{n}_q'
        counts_url_no_all, counts_url_no_all_not_in_q, counts_url_no_st_not2, counts_url_no_st_not2_not_in_q, total_books_st_not2_not_in, counts_url_no_st_none, counts_url_no_st_none_not_in_q, total_books_st_none_not_in = analyze_collection(n)
        print(f'| {collection_name} | {counts_url_no_all:>6} | {counts_url_no_all_not_in_q:>8} | {counts_url_no_st_not2:>14} | {counts_url_no_st_not2_not_in_q:>8} | {total_books_st_not2_not_in:>5} | {counts_url_no_st_none:>14} | {counts_url_no_st_none_not_in_q:>8} | {total_books_st_none_not_in:>5} |')

    total_unique_url_no, url_no_not_in_q_count = analyze_all_collections()
    print(f'|  total   | {total_unique_url_no:>6} | {url_no_not_in_q_count:>8} |')

if __name__ == "__main__":
    stat_books_publicid()

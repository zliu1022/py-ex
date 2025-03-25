#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import pymongo
from pymongo import UpdateOne
import requests
from bs4 import BeautifulSoup

from getq import get_url, login, inc_getqnum
from getonebook_cover import getonebook_cover
from getonebook import getonebook
from getonebook_cover_content import getonebook_cover_content

from pprint import pprint
import time
import random

from config import site_name, base_url, cache_dir, db_name

'''
从mongodb，x库，book_1集合中提取文档,读取id到 book_url_id，

访问cover: base/book/book_url_id/，调用 get_url获取网页
调用getonebook_cover.py，获取book_qnum，book_donenum，book_complete_url
返回cover内容，有时也有q内容，更新到 book_n, 更新到 book_n_q

访问 base/book_complete_url，调用 get_url获取网页，也是第一页
调用 getonebook.py，获取url_level，url_no，total_pagenum
把url_level，url_no，存入 book_n_q 
继续访问... total_pagenum，直到完成

异常
- cover 404: is_share,访问complete
- complete空: 跳过（因为已经通过cover访问过）
'''

def wait_qcounter(counter, rest_num=150):
    if counter == rest_num:
        print(f"Reached {rest_num} calls. Waiting for 10 seconds.")
        time.sleep(10)
        counter = 0  # 重置计数器
    return counter+1

def save_html(response, html_name):
    soup = BeautifulSoup(response.text, 'html.parser')
    pretty_html = soup.prettify()
    with open(html_name, 'w', encoding=response.encoding) as file:
        file.write(pretty_html)
    print(f"html页面保存 {html_name}")

def sanitize_filename(filename):
    # Remove or replace invalid characters
    # Define a set of characters that are invalid in filenames
    invalid_chars = r'[<>:"/\\|?*\']'
    # Replace invalid characters with an underscore or any safe character
    sanitized = re.sub(invalid_chars, '_', filename)
    # Additionally, remove leading and trailing whitespace
    sanitized = sanitized.strip()
    # Optionally, remove sequences like '..' that could represent parent directories
    sanitized = sanitized.replace('..', '_')
    return sanitized

def getonebook_complete(session, book_url_id, book_complete_url):
    print('first', book_complete_url)
    response = get_url(session, book_complete_url)
    if response is None:
        print(f'fail to get complete/first {book_complete_url}')
        quit()
    ret = getonebook(response.text)
    if ret:
        op_num = batch_update(ret['url_contents'], book_url_id, book_complete_url)
    else:
        print(f'fail to decode {book_complete_url}')
        quit()
    print(f'共{ret['total_pagenum']}页')

    begin_page = 2
    # 获取第2-total页
    for i in range(begin_page, ret['total_pagenum']+1):
        next_page_url = book_complete_url + '?page=' + str(i)
        print('next', next_page_url, ret['total_pagenum'])
        response = get_url(session, next_page_url)
        if response is None:
            print(f'fail to get {book_complete_url}')
            quit()
        ret = getonebook(response.text)
        if ret:
            opnum = batch_update(ret['url_contents'], book_url_id, book_complete_url)
        else:
            print(f'fail to decode {book_complete_url}')
            quit()
        getbook_counter = wait_qcounter(getbook_counter)

def batch_update(ret, book_url_id, book_complete_url):
    global book_collection
    global curbook_collection

    operations = []
    for item in ret:
        operations.append(
            UpdateOne(
                { 'url_no': item['url_no'], 'book_id': book_url_id },
                { '$set': { 'url_level': item['url_level'], 'url_frombook': item['url_frombook'] } },
                upsert=True
            )
        )
    op_num = len(operations)
    if operations:
        result = book_collection.bulk_write(operations)
        print(f"匹配 {result.matched_count}, 修改 {result.modified_count}, 新增 {result.upserted_count} {book_complete_url}")
    else:
        print(f'Warning: no operation, empty page {book_complete_url}')
        #curbook_collection.update_one( {'id': book_url_id }, {'$set': { 'comment': '难度页空'}})
    return op_num

def getonebook_content(session, documents):
    global book_collection
    global curbook_collection

    for doc in documents:
        book_url_id = doc['id']
        book_name = doc['name']
        book_content = doc['cover']['content']
        for content in book_content:
            book_url = content['url']
            book_complete_url = base_url + book_url

            response = get_url(session, book_complete_url)
            if response is None:
                print(f'fail to get cover {book_complete_url} is_share?')
                continue
            ret = getonebook_cover_content(response.text)
            if ret:
                op_num = batch_update(ret, book_url_id, book_complete_url)
            else:
                print(f'fail to decode {book_complete_url}')

# 获取一个level的所有book，比如获取book_1，入门的所有棋书
def getbook_level(session, documents):
    global book_collection
    global curbook_collection

    last_id = 0
    last_page = 0
    begin_status = True

    getbook_counter = 0

    for doc in documents:
        book_url_id = doc['id']
        book_name = doc['name']

        if begin_status is False:
            if book_url_id != last_id:
                continue
            else:
                begin_status = True

        # book_cover
        book_url = f'{base_url}/book/{book_url_id}/'
        print('cover', book_url)

        response = get_url(session, book_url)
        if response:
            # 先读cover再存文件,读取失败就不会覆盖上次
            ret, ret_q = getonebook_cover(response.text)

            safe_book_name = sanitize_filename(book_name)
            html_name = cache_dir + "/" + str(book_url_id) + '_' + safe_book_name + '.html'
            save_html(response, html_name)

            if ret:
                curbook_collection.update_one(
                    {'id': book_url_id},
                    {'$set': {
                        'cover': {
                            'qnum':        ret.get('book_qnum'),
                            'level':       ret.get('book_level'),
                            'donenum':     ret.get('book_donenum'),
                            'complete_url': ret.get('book_complete_url'), #ex: '/book/levelorder/361/'
                            'content':     ret.get('book_content')
                            }
                    }}
                )
                print(f'共{ret.get('book_qnum')}题，难度{ret.get('book_level')}')

            if ret_q:
                op_num = batch_update(ret_q, book_url_id, book_url)
        else:
            print(f'fail to get cover {book_url}')

        # book_complete, 第1页
        if response is None or ret is None: # 404 or is_share, try complete
            print(f'Info: {book_url_id} book_cover empty or 404')
            book_complete_url = base_url + '/book/levelorder/' + str(book_url_id) + '/'
        else:
            if ret.get('book_complete_url') != '':
                book_complete_url = base_url + ret.get('book_complete_url')
            else:
                print(f'Info: {book_url_id} book_complete_url empty, make it')
                book_complete_url = base_url + "/book/levelorder/" + str(book_url_id) + "/"

        getonebook_complete(session, book_url_id, book_complete_url)

def getbook(session):
    global book_collection
    global curbook_collection

    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    books = [
        #{'file':"入门.html", 'level':1},
        #{'file':"初级.html", 'level':2},
        #{'file':"中级.html", 'level':3},
        #{'file':"进阶.html", 'level':4},
        {'file':"高级.html", 'level':5}
    ]
    for b in books:
        print(b)
        book_collection = db['book_' + str(b['level']) + '_q']
        book_collection.create_index([('url_no', 1), ('book_id', 1)])

        curbook_collection = db['book_' + str(b['level'])]

        #获取这个level全部书
        #documents = curbook_collection.find({'comment': '难度页空'}, {'_id': 0, 'id': 1, 'name': 1}).sort('id', 1)
        documents = curbook_collection.find({}, {'_id': 0, 'id': 1, 'name': 1}).sort('id', 1)
        data_list = [{'id': doc.get('id'), 'name': doc.get('name')} for doc in documents]
        getbook_level(session, data_list)

        #获取一本book的complete页,以及后续所有页
        #book_url_id = 3764
        #book_complete_url = base_url + '/book/levelorder/' + str(book_url_id) + '/'
        #getonebook_complete(session, book_url_id, book_complete_url)

        #获取book的content 里面!! 内容
        #documents = curbook_collection.find({'comment': '难度页空'}) #10min超时, 需要加no_cursor_timeout=True
        #getonebook_content(session, documents)
        quit()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        username = sys.argv[1]
    else:
        quit()
    session = login(username)

    if session is None:
        print("登录失败")

    getbook(session)


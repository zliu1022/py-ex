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

from pprint import pprint
import time
import random

'''
从mongodb，x库，book_1集合中提取文档
读取id到 book_url_id，

访问 https://www.101weiqi.com/book/book_url_id/，调用 get_url获取网页
调用getonebook_cover.py，获取book_qnum，book_donenum，book_complete_url
更新内容到 book_1 的相应文档中

访问 https://www.101weiqi.com/book_complete_url，调用 get_url获取网页，这也是第一页，通过第一页可以获取到下一页的页码
调用 getonebook.py，获取url_level，url_no，total_pagenum
把url_level，url_no，存入 book_1_q 集合
访问https://www.101weiqi.com/... total_pagenum，直到完成
'''

def wait_qcounter(counter, rest_num=150):
    if counter == rest_num:
        print(f"Reached {rest_num} calls. Waiting for 10 seconds.")
        time.sleep(10)
        counter = 0  # 重置计数器
    '''
    else:
        wait_time = random.randint(1, 2)
        print(f"Waiting for {wait_time} seconds.")
        time.sleep(wait_time)
    '''
    return counter+1

def save_html(response, html_name):
    soup = BeautifulSoup(response.text, 'html.parser')
    pretty_html = soup.prettify()
    with open(html_name, 'w', encoding=response.encoding) as file:
        file.write(pretty_html)
    print(f"html页面保存 {html_name}。")

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

# 获取一个level的所有book，比如获取book_1，入门的所有棋书
def getonebooklevel(session, documents):
    last_id = 57503
    last_page = 0
    begin_status = False

    global username
    global book_collection
    global curbook_collection
    getbook_counter = 0

    book_cover_fail = []
    for doc in documents:
        book_url_id = doc['id']
        book_name = doc['name']

        if begin_status is False:
            if book_url_id != last_id:
                continue
            else:
                begin_status = True
        '''
        # 根据id，判断book库中是否存在同样id，有则跳过
        ret = book_collection.find_one({'book_id': book_url_id})
        if ret:
            continue
        '''

        # book_cover
        book_url = f'https://www.101weiqi.com/book/{book_url_id}/'
        print('cover', book_url)

        response = get_url(session, book_url)
        if response is None:
            book_cover_fail.append(book_url_id)
            print('fail_list', book_cover_fail)
            continue

        safe_book_name = sanitize_filename(book_name)
        html_name = '.cache/' + str(book_url_id) + '_' + safe_book_name + '.html'
        save_html(response, html_name)
        ret = getonebook_cover(response.text)
        '''
        {   'book_name':    book_name,              # 对应book_2的name
            'book_qnum':    book_qnum,              # 对应book_2的ba.qcount
            'book_level':   book_level,             # 对应book_2的ba.qlevelname
            'book_donenum': book_donenum,
            'book_complete_url': book_complete_url, # 形如/book/levelorder/361/，但21744却为空
            'book_content':
                {   'no':   content_no,
                    'url':  content_url,
                    'name': content_name,
                    'num':  content_num } }
        '''
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

        # book_complete, 第1页
        if ret.get('book_complete_url') != '':
            book_complete_url = 'https://www.101weiqi.com' + ret.get('book_complete_url')
        else:
            print(f'Info: {book_url_id} book_complete_url empty')
            book_complete_url = 'https://www.101weiqi.com/book/levelorder/' + str(book_url_id) + '/'
        print('first', book_complete_url)
        response = get_url(session, book_complete_url)
        if response is None:
            book_cover_fail.append(book_url_id)
            print('fail_list', book_cover_fail)
            continue
        ret = getonebook(response.text)
        '''
        {   'book_title':    book_title,    # 就是name
            'total_pagenum': total_pagenum, # 用这个
            'cur_pagenum':   cur_pagenum,   # 没用
            'next_pagenum':  next_pagenum,  # 没用
            'url_contents': [
                {
                    'url_level':    url_level,
                    'url_no':       url_no,
                    'url_frombook': url    # 从book_url进入的索引序号,ex:'/book/levelorder/361/1/'
                } }
        '''
        '''
        for item in ret['url_contents']:
            book_collection.update_one(
                { 'url_no': item['url_no'], 'book_id': book_url_id },
                { '$set': { 'url_level': item['url_level'], 'url_frombook': item['url_frombook'] } },
                upsert=True
            )
        '''
        operations = []
        for item in ret['url_contents']:
            operations.append(
                UpdateOne(
                    { 'url_no': item['url_no'], 'book_id': book_url_id },
                    { '$set': { 'url_level': item['url_level'], 'url_frombook': item['url_frombook'] } },
                    upsert=True
                )
            )
        if operations:
            result = book_collection.bulk_write(operations)
            print(f"匹配 {result.matched_count}, 修改 {result.modified_count}, 新增 {result.upserted_count}")
        else:
            pprint(ret)
            print(operations)
            print(f'Warning: no operation, empty page {book_complete_url}')
            curbook_collection.update_one(
                {'id': book_url_id },
                {'$set': { 'comment': '难度页空'}}
            )

        print(f'共{ret['total_pagenum']}页')

        begin_page = 2
        if book_url_id == last_id and last_page != 0:
            begin_page = last_page+1

        # 获取第2-total页
        for i in range(begin_page, ret['total_pagenum']+1):
            next_page_url = book_complete_url + '?page=' + str(i)
            print('next', next_page_url, ret['total_pagenum'])
            response = get_url(session, next_page_url)
            inc_getqnum(username)
            if response is None:
                book_cover_fail.append(book_url_id)
                print('fail_list', book_cover_fail)
                quit()
            ret = getonebook(response.text)
            '''
            for item in ret['url_contents']:
                book_collection.update_one(
                    { 'url_no': item['url_no'], 'book_id': book_url_id },
                    { '$set': { 'url_level': item['url_level'], 'url_frombook': item['url_frombook'] } },
                    upsert=True
                )
            '''
            operations = []
            for item in ret['url_contents']:
                operations.append(
                    UpdateOne(
                        { 'url_no': item['url_no'], 'book_id': book_url_id },
                        { '$set': { 'url_level': item['url_level'], 'url_frombook': item['url_frombook'] } },
                        upsert=True
                    )
                )
            if operations:
                result = book_collection.bulk_write(operations)
                print(f"匹配 {result.matched_count}, 修改 {result.modified_count}, 新增 {result.upserted_count}")
            else:
                pprint(ret)
                print(operations)
                quit()

            getbook_counter = wait_qcounter(getbook_counter)

def getbook(session):
    global book_collection
    global curbook_collection

    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['101']

    books = [
        #{'file':"入门.html", 'level':1},
        {'file':"初级.html", 'level':2},
        {'file':"中级.html", 'level':3},
        {'file':"进阶.html", 'level':4},
        {'file':"高级.html", 'level':5}
    ]
    for b in books:
        print(b)
        book_collection = db['book_' + str(b['level']) + '_q']
        book_collection.create_index([('url_no', 1), ('book_id', 1)])

        curbook_collection = db['book_' + str(b['level'])]
        #documents = curbook_collection.find(), 10min超时, 需要加no_cursor_timeout=True
        documents = curbook_collection.find({}, {'_id': 0, 'id': 1, 'name': 1})
        data_list = [{'id': doc.get('id'), 'name': doc.get('name')} for doc in documents]

        getonebooklevel(session, data_list)
        quit()

if __name__ == "__main__":
    username = '33excited@indigobook.com'
    session = login(username)

    if session is None:
        print("登录失败")

    getbook(session)


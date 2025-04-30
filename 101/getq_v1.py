#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from pymongo import MongoClient, ReturnDocument
from datetime import datetime, timedelta
from requests.cookies import RequestsCookieJar
import sys
from bs4 import BeautifulSoup
import re
import json
import base64
from matchq import canonicalize_positions
from bson import ObjectId
from config import site_name, base_url, cache_dir, db_name, headers_get, headers_login
import time

def login(mongo_client, username):
    db = mongo_client[db_name]
    login_collection = db["login"]

    # 创建用户名唯一索引（如果不存在）
    login_collection.create_index('username', unique=True)

    # 从MongoDB中获取对应username的记录
    login_data = login_collection.find_one({'username': username})

    if login_data:
        password = login_data.get('password')
        # 检查session的时间是否在一天之内
        session_time_str = login_data.get('timestamp')
        if session_time_str:
            session_time = datetime.strptime(session_time_str, '%Y-%m-%d %H:%M:%S')
            if datetime.now() - session_time < timedelta(days=999):
                # 从存储的cookies中重建session
                session_cookies = login_data.get('cookies')
                if session_cookies:
                    session = requests.Session()
                    jar = RequestsCookieJar()
                    for cookie in session_cookies:
                        jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
                    session.cookies = jar
                    print(f"使用存储的session，用户名：{username}。")
                    return session
        else:
            print("存储的session已过期，重新登录。")
    else:
        print(f"未找到用户名为'{username}'的记录。")
        password = input('请输入密码：')

    # 执行登录操作
    login_url = base_url + "/login/"

    data = {
        "source": "index_nav",
        'form_username': username,
        'form_password': password
    }
    session = requests.Session()
    response = session.post(login_url, data=data, headers=headers_login)

    if response.status_code == 200:
        # 检查登录是否成功
        soup = BeautifulSoup(response.text, 'html.parser')
        # 查找id为'curuser'的<input>元素
        curuser_input = soup.find('input', {'id': 'curuser'})
        if curuser_input and curuser_input.get('value'):
            logged_in_username = curuser_input.get('value')
            print(f"登录成功，用户名：{logged_in_username}")
            print("登录成功，保存session。")
            # 提取cookie并保存到MongoDB
            session_cookies = []
            for cookie in session.cookies:
                session_cookies.append({
                    'name': cookie.name,
                    'value': cookie.value,
                    'domain': cookie.domain,
                    'path': cookie.path,
                    'expires': cookie.expires,
                    'secure': cookie.secure,
                    'rest': cookie._rest,
                    'rfc2109': cookie.rfc2109,
                })

            # 更新或插入用户名的cookies和时间戳到MongoDB
            login_collection.update_one(
                {'username': username},
                {'$set': {
                    'password': password,
                    'cookies': session_cookies,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }},
                upsert=True
            )
            return session
        else:
            print("登录失败，请检查您的用户名和密码")
            return None
    else:
        print("登录请求失败，状态码：", response.status_code)
        return None

def get_url(session, url):
    response = session.get(url, headers=headers_get)
    if response.status_code == 200:
        return response
    else:
        print(f"获取URL失败，状态码：{response.status_code}")
        return None

def get_url_v1(session, url, max_retries=3, delay=3):
    for attempt in range(max_retries):
        try:
            response = session.get(url, headers=headers_get, timeout=120)
            if response.status_code == 200:
                return response
            elif response.status_code == 502:
                print(f"请求失败（502 Bad Gateway），重试 {attempt + 1}/{max_retries} 次")
                time.sleep(delay)
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return response
        except requests.RequestException as e:
            print(f"请求异常：{e}")
            response = requests.Response()
            response.status_code = 600  # 自定义状态码，表示请求异常
            return response
    print(f"多次重试失败，放弃，状态码：{response.status_code}")
    return response

def decode_prepos(c, r):
    # one0one333 = atob("MTAx") + (obj['c']+1)
    r_str = str(r + 1)
    salt = db_name + r_str + r_str + r_str
    
    n = base64.b64decode(c).decode('utf-8')
    l = 0
    i = []
    for o in range(len(n)):
        i.append(chr(ord(n[o]) ^ ord(salt[l])))
        l = (l + 1) % len(salt)
    result = ''.join(i)
    json_ret = json.loads(result)
    return json_ret

def answer_type(ty):
    if ty == 1:
        type_ = '正解'
    elif ty == 3:
        type_ = '失败'
    elif ty == 2:
        type_ = '变化'
    elif ty == 4:
        type_ = '淘汰'
    else:
        type_ = '未知'
    return type

def answer_status(st):
    if st == 2:
        status = '审完'
    elif st == 1:
        status = '待审'
    else:
        status = '未知'
    return status

def resp_json(mongo_client, resp, level_str, no):
    title_id = ""
    title_level = ""

    #version1:
    #match = re.search(r'<title>Q-(\d+) -', resp.text)
    #version2:
    #match = re.search(r'<title>Q-(\d+) - (\d+[KDKP]) -', resp.text)
    #    title_id = match.group(1)       # 提取 "22004"
    #    title_level = match.group(2)    # 提取 "9K"

    pattern = r"<title>\s*Q-(\d+)\s*-\s*(\S+?)\s*-"
    match = re.search(pattern, resp.text, re.S)
    if match:
        title_id = match.group(1)
        title_level = match.group(2)
        print('html title', title_id, title_level)
        if title_id != no:
            #url_no和实际id不一致，url_level不一致，只要是公开，还是会跳转
            #publicid可能是当前id，但没进行publicid和title_id一致检查，title_id只具有参考性质
            print(f'warning title_id {title_level} {title_id} != url_no {no}')
            insert_level_urlno(mongo_client, title_level, title_id)
    else:
        #如果没有跳转到404，如果已经封杀，跳转到首页
        print('warning match title failed {level_str} {no}')
        quit()

    # 提取js变量
    #re.DOTALL 标志使 . 可以匹配包括换行符在内的所有字符。
    #.*? 是非贪婪匹配，尽可能少地匹配字符，直到找到第一个 };。
    pattern = r'var\s+g_qq\s*=\s*\{.*?\};'
    match = re.search(pattern, resp.text, re.DOTALL)
    if match:
        g_qq_str = match.group()
        json_str = g_qq_str[11:-1] # 去除开头的 var g_qq =，以及最后的分号
        try:
            obj = json.loads(json_str)
        except json.JSONDecodeError:
            print(f'Failed to decode json: {json_str}')
            return {'ret': False, 'code': 2}
    else:
        print(f'Failed to find g_qq: {no}')
        return {'ret': False, 'code': 1}

    json_name  = cache_dir + "/" + no + '-' + title_id + '-g_qq.json'
    with open(json_name, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

    if obj.get('is_public') == False:
        new_doc_id = ObjectId()
        stones_key_list = [['_invalid_', str(new_doc_id)]]
        doc = {
            'url_no':     no,
            'url_level':  level_str,
            'title_id':   title_id,
            'min_pp':     stones_key_list
        }
        print(f'Not public, insert empty p: {no} {title_id}')
        return {'ret': True, 'data': doc}

    if obj.get('status') != 2:
        print(f'status != 2 {no}')

    prepos = decode_prepos(obj.get('c'), obj.get('r'))

    # 对每个字符串进行字符位置交换
    if obj.get('xv') and obj.get('xv') % 3 != 0:
        swapped_prepos = [[s[1] + s[0] if len(s) == 2 else s for s in sublist] for sublist in prepos]
        prepos = swapped_prepos

    prepos_json = {   
        'b': prepos[0],
        'w': prepos[1]
    }
    stones_key = canonicalize_positions(prepos_json)
    stones_key_list = [list(item) for item in stones_key]
    stones_key_json = json.dumps(stones_key_list, sort_keys=True)

    ans = []
    for an in obj['answers']:
        if an['ty'] == 1 or an['ty'] == 2 and an['st'] == 2:
            anseq = []
            for p in an['pts']:
                anseq.append(p['p'])
            e = {
                'ty': an['ty'],
                'st': an['st'],
                'p':  anseq
            }
            ans.append(e)

    doc = {
        'url_no':     no,
        'url_level':  level_str,
        'title_id':   title_id,
        'id':         obj.get('id'),
        'publicid':   obj.get('publicid'), #唯一id，但不一定能通过level/id访问
        'size':       obj.get('lu'),
        'status':     obj.get('status'), # 0未入库，1被淘汰，2正常
        'c':          obj.get('c'),
        'r':          obj.get('r'),
        'xv':         obj.get('xv'),
        'prepos':     prepos_json, 
        'min_pp':     stones_key_json,
        'title':      obj.get('title'),
        'blackfirst': obj.get('blackfirst'),
        'qtype':      obj.get('qtypename'),
        'level':      obj.get('levelname'), #level
        'name':       obj.get('name'),
        'signs':      obj.get('signs'), # 需要同时显示，比如三角形
        'options':    obj.get('options'),
        'answers':    ans,
        'stat':       obj.get('taskresult'),
        'similar':    obj.get('sms_count'),
        'bookinfos':    obj.get('bookinfos')
    }

    return {'ret': True, 'data': doc}

# 分析title_id和url_no不一致，更新level集合
def insert_level_urlno(mongo_client, level_str, url_no):
    db = mongo_client[db_name]
    collection = db['level']

    docs = collection.find({'level': level_str})
    for doc in docs:
        if 'list' in doc and url_no in doc['list']:
            # url_no already in list, do nothing
            print(f'{url_no} existing in level {level_str} table')
            continue
        else:
            collection.update_one(
                {'_id': doc['_id']},
                {'$push': {'list': url_no}}
            )
            print(f'insert to level {level_str} table')

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

def inc_getqnum(mongo_client, username):
    db = mongo_client[db_name]
    login_collection = db["login"]
    ret = login_collection.update_one(
        {'username': username},
        {'$inc': {'getq_num': 1}},
        upsert=True # 如果文档不存在则创建
    )
    return ret

def update_q(mongo_client, doc):
    db = mongo_client[db_name]
    collection = db['q']

    filter = {'min_pp': doc['min_pp']}
    old = collection.find_one_and_replace(
        filter=filter,
        replacement=doc,
        upsert=True,
        return_document=ReturnDocument.BEFORE  # 返回更新前的文档
    )

    if old:
        # 删除 '_id' 字段以避免比较中出现
        old.pop('_id', None)

        differences = dict_diff(old, doc)
        if differences:
            print("以下字段已被更新：")
            for field, change in differences.items():
                if field == 'stat.fail_nums' or field == 'stat.ok_nums' or field == 'r' or field == 'xv':
                    continue
                elif field == 'c':
                    print(f"{field}: 从 {change['old'][0:10]} 更新为 {change['new'][0:10]}")
                else:
                    print(f"{field}: 从 {change['old']} 更新为 {change['new']}")
        else:
            print("数据已存在，且无任何变化。")

def update_q_v1(client, doc):
    db = client[db_name]
    collection = db['q']

    filter = {'min_pp': doc['min_pp']}
    old = collection.find_one(filter)  # 获取更新前的文档
    # 插入数据只有：正常；
    # 其他数据不进入q库，写book_q库：404/502等，is_share
    if old is None:
        collection.insert_one(doc)
        print("插入q表", doc['publicid'], doc['level'])
        return 0

    # 仅更新提供的字段
    update_data = {k: v for k, v in doc.items() if v is not None}
    new = collection.find_one_and_update(
        filter=filter,
        update={"$set": update_data},
        upsert=True,  # 如果不存在则插入
        return_document=ReturnDocument.AFTER  # 返回更新后的文档
    )

    # 删除 '_id' 字段，避免比较干扰
    old.pop('_id', None)
    new.pop('_id', None)

    # 计算差异
    differences = dict_diff(old, new)
    if differences:
        print("以下字段已被更新", doc['publicid'], doc['level'])
        for field, change in differences.items():
            if field in {'stat.fail_nums', 'stat.ok_nums', 'r', 'xv'}:
                continue
            elif field == 'c':
                print(f"{field}: 从 {change['old'][0:10]} 更新为 {change['new'][0:10]}")
            else:
                print(f"{field}: 从 {change['old']} 更新为 {change['new']}")
    else:
        print("数据已存在，且无任何变化。")
    return 1

def resp_json_url_frombook(mongo_client, resp_text, url_frombook):
    title_id = None
    title_level = None
    pattern = r"<title>\s*Q-(\d+)\s*-\s*(\S+?)\s*-"
    match = re.search(pattern, resp_text, re.S)
    if match:
        title_id = match.group(1)
        title_level = match.group(2)
        print('html提取 id和level', title_id, title_level)

    # 提取js变量
    #re.DOTALL 标志使 . 可以匹配包括换行符在内的所有字符。
    #.*? 是非贪婪匹配，尽可能少地匹配字符，直到找到第一个 };。
    pattern = r'var\s+g_qq\s*=\s*\{.*?\};'
    match = re.search(pattern, resp_text, re.DOTALL)
    if match:
        g_qq_str = match.group()
        json_str = g_qq_str[11:-1] # 去除开头的 var g_qq =，以及最后的分号
        try:
            obj = json.loads(json_str)
        except json.JSONDecodeError:
            print(f'Failed to decode json: {json_str}')
            quit()
            return {'ret': False, 'code': 2}
    else:
        print(f'Failed to find g_qq: {url_frombook}')
        return {'ret': False, 'code': 1}

    if obj.get('is_public') == False:
        print(f'Not public {url_frombook} {title_id}')
        return {'ret': False, 'code': 3}

    if obj.get('status') != 2:
        # status：0审核，1淘汰，2入库, 大量!=2可能异常
        print(f'Info: status != 2 {url_frombook}')

    prepos = decode_prepos(obj.get('c'), obj.get('r'))

    # 对每个字符串进行字符位置交换
    if obj.get('xv') and obj.get('xv') % 3 != 0:
        swapped_prepos = [[s[1] + s[0] if len(s) == 2 else s for s in sublist] for sublist in prepos]
        prepos = swapped_prepos

    prepos_json = {   
        'b': prepos[0],
        'w': prepos[1]
    }
    stones_key = canonicalize_positions(prepos_json)
    stones_key_list = [list(item) for item in stones_key]
    stones_key_json = json.dumps(stones_key_list, sort_keys=True)

    ans = []
    for an in obj['answers']:
        if an['ty'] == 1 or an['ty'] == 2 and an['st'] == 2:
            anseq = []
            for p in an['pts']:
                anseq.append(p['p'])
            e = {
                'ty': an['ty'],
                'st': an['st'],
                'p':  anseq
            }
            ans.append(e)

    doc = {
        'publicid':   obj.get('publicid'),  #唯一id，但不一定能通过level/id访问
        'status':     obj.get('status'),    # 0未入库，1被淘汰，2正常
        'level':      obj.get('levelname'), #level
        'qtype':      obj.get('qtypename'),
        'blackfirst': obj.get('blackfirst'),
        'c':          obj.get('c'),
        'r':          obj.get('r'),
        'xv':         obj.get('xv'),
        'prepos':     prepos_json, 
        'min_pp':     stones_key_json,
        'answers':    ans,
        'stat':       obj.get('taskresult'),
        'similar':    obj.get('sms_count'),
        'bookinfos':    obj.get('bookinfos'),
        'size':       obj.get('lu'),
        'title_id':   title_id,
        'id':         obj.get('id'),
        'title':      obj.get('title'),
        'name':       obj.get('name'),
        'signs':      obj.get('signs'), # 需要同时显示，比如三角形
        'options':    obj.get('options')
    }

    return {'ret': True, 'data': doc}

#q库唯一索引只有minpp
#从url_level, url_no抓取，就更新url_level, url_no
#从url_frombook抓取，就更新url_frombook
def getq_url_frombook(mongo_client, session, book_q_str, url_frombook):
    db = mongo_client[db_name]
    book_q_collection = db[book_q_str]

    url = base_url + url_frombook
    response = get_url_v1(session, url)
    if response.status_code == 200:
        ret = resp_json_url_frombook(mongo_client, response.text, url_frombook)
        if ret.get('ret'):
            # 成功：更新q表，更新book_n_q表, 不锁定book_n_q表，确保一本book_id只有一个任务
            retcode = update_q_v1(mongo_client, ret.get('data')) # 0:新增,1:更新
            result = book_q_collection.update_one(
                {'url_frombook': url_frombook},
                {'$set': {
                    'publicid': ret.get('data').get('publicid'), 
                    'min_pp':   ret.get('data').get('min_pp'), 
                    'status':   ret.get('data').get('status')
                }}
            )
            return {'ret': True, 'data': ret.get('data'), 'code': retcode}
        else:
            # 失败：只更新book_n_q表, is_share
            print(f"不共享，{url_frombook}")
            result = book_q_collection.update_one(
                {'url_frombook': url_frombook},
                {'$set': {'status': 600 + ret.get('code')*100}}
            )
            return {'ret': False, 'code': 1 + ret.get('code'), 'message':'不共享'}
    else:
        # 失败：只更新book_n_q表
        print(f"获取页面失败，{url_frombook}")
        result = book_q_collection.update_one(
            {'url_frombook': url_frombook},
            {'$set': {'status': response.status_code}}
        )
        return {'ret': False, 'code': 1, 'message':'获取页面失败'}

def getq(mongo_client, username, level_str, no):
    url = base_url + "/" + level_str + "/" + no
    html_name = cache_dir + "/" + no + ".html"

    session = login(mongo_client, username)
    if session is None:
        print("登录失败，无法继续。")
        return {'ret': False, 'code': 2, 'message':'登录失败'}

    response = get_url(session, url)
    inc_getqnum(mongo_client, username)
    if response:
        soup = BeautifulSoup(response.text, 'html.parser')
        pretty_html = soup.prettify()
        with open(html_name, 'w', encoding=response.encoding) as file:
            file.write(pretty_html)

        ret = resp_json(mongo_client, response, level_str, no)
        if ret.get('ret'):
            update_q(mongo_client, ret.get('data'))
            return {'ret': True, 'data': ret.get('data')}
        else:
            return {'ret': False, 'code': 3, 'message':'解析json失败'}
    else:
        # 404，插入空记录，网络失败可能也是这个
        new_doc_id = ObjectId()
        stones_key_list = [['_invalid_', str(new_doc_id)]]
        err_json = {
            'url_no':    no,
            'url_level':    level_str,
             "status":   404,
            'min_pp':    stones_key_list
        }
        update_q(mongo_client, err_json)
        print(f"无法获取页面内容, 插入404，{no}")
        return {'ret': False, 'code': 1, 'message':'获取页面失败'}

if __name__ == "__main__":
    if len(sys.argv) == 4:
        username = sys.argv[1]
        level_str = sys.argv[2]
        url_no = sys.argv[3]
    else:
        print('command:')
        print('getq username level_str url_no')
        quit()
    mongo_client = MongoClient("mongodb://localhost:27017/")
    getq(mongo_client, username, level_str, url_no)
    mongo_client.close()

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
from config import site_name, base_url, cache_dir

def login(username):
    # MongoDB连接参数
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["101"]
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
            if datetime.now() - session_time < timedelta(days=1):
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
    headers = {
        "authority": site_name,
        "method": "POST",
        "path": "/login/",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh,en;q=0.9,zh-CN;q=0.8",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
        "dnt": "1",
        "origin": base_url,
        "pragma": "no-cache",
        "referer": base_url,
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    }

    data = {
        "source": "index_nav",
        'form_username': username,
        'form_password': password
    }
    session = requests.Session()
    response = session.post(login_url, data=data, headers=headers)

    if response.status_code == 200:
        #print("登录请求成功。")

        # 检查登录是否成功
        if "登录失败" in response.text or "密码错误" in response.text:
            print("登录失败，请检查您的用户名和密码。")
            return None
        else:
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
        print("登录请求失败，状态码：", response.status_code)
        return None

def get_url(session, url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    response = session.get(url, headers=headers)
    if response.status_code == 200:
        #print("成功获取URL内容。")
        return response
    else:
        print(f"获取URL失败，状态码：{response.status_code}")
        return None

def decode_prepos(c, r):
    # 101333 = atob("MTAx") + (obj['c']+1)
    r_str = str(r + 1)
    salt = "101" + r_str + r_str + r_str
    
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

def resp_json(resp, level_str, no):
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
            print(f'warning title_id {title_level} {title_id} != url_no {no}')
            insert_level_urlno(title_level, title_id)
    else:
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

    json_name  = cache_dir + no + '-' + title_id + '-g_qq.json'
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
        print(f'Not public, insert empty p: {no}')
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
        'publicid':   obj.get('publicid'),
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
        'level':      obj.get('levelname'),
        'name':       obj.get('name'),
        'options':    obj.get('options'),
        'answers':    ans,
        'stat':       obj.get('taskresult'),
        'similar':    obj.get('sms_count'),
        'bookinfos':    obj.get('bookinfos')
    }

    return {'ret': True, 'data': doc}

# 分析title_id和url_no不一致，更新level集合
def insert_level_urlno(level_str, url_no):
    client = MongoClient()
    db = client['101']
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
    client.close()

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

def inc_getqnum(username):
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["101"]
    login_collection = db["login"]
    ret = login_collection.update_one(
        {'username': username},
        {'$inc': {'getq_num': 1}},
        upsert=True # 如果文档不存在则创建
    )
    mongo_client.close()
    return ret

def update_q(doc):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['101']
    collection = db['q']
    #collection.create_index('no', unique=True)

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
    else:
        print(f"q集合插入新文档 {doc['url_no']}")
    client.close()

def getq(level_str, no):
    url = base_url + level_str + "/" + no
    html_name = cache_dir + no + ".html"

    session = login(username)
    if session:
        response = get_url(session, url)
        inc_getqnum(username)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            pretty_html = soup.prettify()
            with open(html_name, 'w', encoding=response.encoding) as file:
                file.write(pretty_html)
            #print(f"页面已保存到 {html_name}。")

            ret = resp_json(response, level_str, no)
            if ret.get('ret'):
                update_q(ret.get('data'))
                return {'ret': True, 'data': ret.get('data')}
            else:
                return {'ret': False, 'code': 3, 'message':'解析json失败'}
        else:
            # 如果404，估计也需要插入空记录，担心网络失败也是这样, 103905, 108916
            new_doc_id = ObjectId()
            stones_key_list = [['_invalid_', str(new_doc_id)]]
            err_json = {
                'url_no':    no,
                'url_level':    level_str,
                 "status":   404,
                'min_pp':    stones_key_list
            }
            update_q(err_json)
            print(f"无法获取页面内容, 插入404，{no}")
            return {'ret': False, 'code': 1, 'message':'获取页面失败'}
    else:
        print("登录失败，无法继续。")
        return {'ret': False, 'code': 2, 'message':'登录失败'}

if __name__ == "__main__":
    level_str = ''
    url_no = ''
    if len(sys.argv) == 3:
        level_str = sys.argv[1]
        url_no = sys.argv[2]
    elif len(sys.argv) == 2:
        url_no = sys.argv[1]
    else:
        print('command:')
        print('getq level_str url_no')
        print('getq url_no (level_str=q)')
        quit()
    getq(level_str, url_no)

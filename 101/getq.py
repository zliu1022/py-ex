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
from pprint import pprint

def login():
    # MongoDB连接参数
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["101"]
    login_collection = db["login"]

    # 从MongoDB中获取session数据
    login_data = login_collection.find_one({})

    if login_data:
        # 检查session的时间是否在一天之内
        session_time_str = login_data['timestamp']
        session_time = datetime.strptime(session_time_str, '%Y-%m-%d %H:%M:%S')
        if datetime.now() - session_time < timedelta(days=1):
            # 从存储的数据中重建session
            session_cookies = login_data['cookies']
            session = requests.Session()
            jar = RequestsCookieJar()

            for cookie in session_cookies:
                jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
            session.cookies = jar
            print("使用存储的session。")
            return session
        else:
            print("存储的session已过期，重新登录。")
    else:
        print("未找到存储的session，进行登录。")

    # 执行登录操作
    login_url = "https://www.101weiqi.com/login/"

    headers = {
        "authority": "www.101weiqi.com",
        "method": "POST",
        "path": "/login/",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh,en;q=0.9,zh-CN;q=0.8",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded",
        "cookie": "csrftoken=E2sOo7ibFaS05ThNBqBGEXx72fIINxsWP3brB5NDPYkWXQAS6J2gTI9zW8AegOZv",
        "dnt": "1",
        "origin": "https://www.101weiqi.com",
        "pragma": "no-cache",
        "referer": "https://www.101weiqi.com/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    }

    data = {
        "csrfmiddlewaretoken": "j7uxusoV2TEmcvpOyDnx4eA07UMlbuV4u8daHqTncH6i4sIT3WO7jZcs1NERELsD",
        "source": "index_nav",
        "form_username": "zliu1022",
        "form_password": "zliu123"
    }

    session = requests.Session()
    response = session.post(login_url, data=data, headers=headers)

    if response.status_code == 200:
        print("登录请求成功。")

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

            # 保存cookies和时间戳到MongoDB
            login_collection.delete_many({})  # 清空集合中的旧数据
            login_collection.insert_one({
                'cookies': session_cookies,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
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
        print("成功获取URL内容。")
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

def resp_json(resp, no):
    match = re.search(r'var g_qq = (.*);', resp.text, re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        print("Pattern not found in the response.")
        quit()

    json_parts = json_str.split(';')

    # 只有第一块是g_qq，后面都是些单行的var定义
    try:
        obj = json.loads(json_parts[0])
    except json.JSONDecodeError:
        print(f'Failed to decode part: {json_parts}')

    with open(no+'-g_qq.json', 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=4)

    prepos = decode_prepos(obj['c'], obj['r'])

    opt = []
    for opt in obj['options']:
        e = {
            'indexname': opt['indexname'],
            'content':   opt['content'],
            'isok':      opt['isok']
        }
        opt.append(e)

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
        'no':         no,
        'size':       obj.get('lu'),
        'prepos':     {
            'b': prepos[0],
            'w': prepos[1]
            },
        'title':      obj.get('title'),
        'blackfirst': obj.get('blackfirst'),
        'qtype':      obj.get('qtypename'),
        'level':      obj.get('levelname'),
        'name':       obj.get('name'),
        'options':    opt,
        'answers':    ans,
        'stat':       obj.get('taskresult'),
        'similar':    obj.get('sms_count')
    }

    return doc

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

def update_q(doc):
    client = MongoClient("mongodb://localhost:27017/")
    db = client['101']
    collection = db['q']

    collection.create_index('no', unique=True)

    filter = {'no': doc['no']}
    old = collection.find_one_and_replace(
        filter=filter,
        replacement=doc,
        upsert=True,
        return_document=ReturnDocument.BEFORE  # 返回更新前的文档
    )

    if old:
        differences = dict_diff(old, doc)
        if differences:
            print("以下字段已被更新：")
            for field, change in differences.items():
                print(f"{field}: 从 {change['old']} 更新为 {change['new']}")
        else:
            print("数据已存在，且无任何变化。")
    else:
        print("已插入新文档。")

def main():
    base_url = "https://www.101weiqi.com/"
    level_str = "q"
    no = 1

    if len(sys.argv) == 2:
        no = sys.argv[1]
    url = base_url + level_str + "/" + no
    html_name = level_str + "-" + no + ".html"
    sgf_name  = level_str + "-" + no + ".sgf"

    session = login()
    if session:
        response = get_url(session, url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            pretty_html = soup.prettify()
            with open(html_name, 'w', encoding=response.encoding) as file:
                file.write(pretty_html)
            print(f"页面已保存到 {html_name}。")

            doc = resp_json(response, no)
            update_q(doc)
        else:
            print("无法获取页面内容。")
    else:
        print("登录失败，无法继续。")

if __name__ == "__main__":
    main()

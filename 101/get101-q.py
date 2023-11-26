#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import json
from pprint import pprint
import sys

#
# 获取9K 第1题，4958，不需要登录
# 所有分支都是正解
# 另存为sgf

base_url = "https://www.101weiqi.com/"

import base64

def testcdata(e, t):
    n = base64.b64decode(e).decode('utf-8')
    r = 0
    i = []
    for o in range(len(n)):
        i.append(chr(ord(n[o]) ^ ord(t[r])))
        r = (r + 1) % len(t)
    return ''.join(i)

def login():
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

    login_url = "https://www.101weiqi.com/login/"
    session = requests.Session()
    response = session.post(login_url, data=data, headers=headers)
    return session

def print_resp_detail(response, session):
    print('session')
    print(response.headers.get('Set-Cookie'))
    print(response.cookies.get('sessionid'))
    print(session.cookies.get('sessionid'))

    #HTTP状态代码（例如，200表示成功，404表示未找到）。
    print('status_code')
    print(response.status_code)

    #响应头，它是一个字典，包含了响应的所有HTTP头。例如，你可以使用 response.headers['content-type'] 来获取响应的 Content-Type 头。
    print('headers')
    print(response.headers)

    #一个 RequestsCookieJar 对象，包含了服务器发送的所有cookies。你可以像字典一样使用它，例如 response.cookies['sessionid']。
    print('cookies')
    print(response.cookies)

    #请求的URL。
    print('url')
    print(response.url)

    #如果请求被重定向，这个属性将包含一个 Response 对象列表，表示重定向历史。第一个对象是最初的请求，最后一个对象是最终的请求。
    print('history')
    print(response.history)

    #一个表示请求花费的时间的 timedelta 对象。
    print('elapsed')
    print(response.elapsed)

    #如果响应的内容是JSON，你可以使用这个方法将其解析为Python字典。
    #print(response.json())

    #响应的原始二进制内容。
    #print(response.content)

    #响应内容的字符串表示，由 response.encoding 所定义的编码解码。
    #print(response.text)

def getq_sess(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    resp = session.get(url, headers=headers)
    return resp

def print_g_qq(obj):
    '''
    status: <class 'int'>
    pos_y1: <class 'int'>
    pos_y2: <class 'int'>
    islei: <class 'bool'>
    myoper: <class 'dict'>, length: dict_keys(['mystar', 'tags', 'mytags'])
    layoutnumber: <class 'int'>
    qshids: <class 'list'>, length: 0
    userlevel: <class 'int'>
    orgid: <class 'int'>
    signs: <class 'list'>, length: 0
    vote: <class 'float'>
    bookinfos: <class 'list'>, length: 5
    xv: <class 'int'>
    id: <class 'int'>
    fine_status: <class 'int'>
    publicid: <class 'int'>
    ineb: <class 'bool'>
    comments: <class 'list'>, length: 32
    specs: <class 'list'>, length: 0
    points: <class 'list'>, length: 0
    max_levelname: <class 'str'>
    hasspec: <class 'bool'>
    luozis: <class 'list'>, length: 0
    username: <class 'str'>
    pos_x2: <class 'int'>
    pos_x1: <class 'int'>
    andata: <class 'dict'>, length: dict_keys(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58'])
    edit_count: <class 'int'>
    sy: <class 'int'>
    is_share: <class 'bool'>
    min_levelname: <class 'str'>
    taskresult: <class 'dict'>, length: dict_keys(['ok_nums', 'ok_total', 'fail_nums', 'fail_total'])
    hasbook: <class 'bool'>
    issingle: <class 'bool'>
    sms_count: <class 'int'>
    nexterrorurl: <class 'str'>
    enable_answer: <class 'bool'>
    ans_count: <class 'int'>
    userid: <class 'int'>
    is_public: <class 'bool'>
    sx: <class 'int'>
    disuse: <class 'int'>
    isguess: <class 'bool'>
    prepos: <class 'list'>, length: 2
    myan: <class 'NoneType'>
    '''
    for k in obj.keys():
        v = obj[k]
        if type(v) is list:
                print(f'{k}: {type(v)}, length: {len(v)}')
        elif type(v) is dict:
                print(f'{k}: {type(v)}, length: {v.keys()}')
        else:
                print(f'{k}: {type(v)}')

    #title: <class 'str'>
    print(obj['title'])
    #qtypename: <class 'str'>
    print(obj['qtypename'])
    #name: <class 'str'>
    print(obj['name'])

    #var typename = ['未知0', '死活题', '手筋题', '定式题', '布局题', '官子题', '未知6', '未知7', '欣赏题', '骗招题', '中盘作战题', '模仿题', '棋理题', '布局猜子题', '中盘猜子题', '官子猜子题', '落子题', '吃子题'];
    #qtype: <class 'int'>
    print(obj['qtype'])
    #options: <class 'list'>, length: 0
    print(obj['options'])
    #answers: <class 'list'>, length: 23
    #print(obj['answers'])
    #attr_type: <class 'int'>
    print(obj['attr_type'])
    #taotaiid: <class 'int'>
    print(obj['taotaiid'])
    #xuandians: <class 'list'>, length: 0
    print(obj['xuandians'])

    #levelname: <class 'str'>
    print(obj['levelname'])


def resp_sgf(resp, url):
    match = re.search(r'var g_qq = (.*);', resp.text)
    json_str = match.group(1)

    json_parts = json_str.split(';')

    # 只有第一块是g_qq，后面都是些单行的var定义
    try:
        obj = json.loads(json_parts[0])
    except json.JSONDecodeError:
        print(f'Failed to decode part: {json_parts}')

    #print_g_qq(obj)

    #lu: <class 'int'>
    #r: <class 'int'>
    #c: <class 'str'>
    #blackfirst: <class 'bool'>

    sgf_str = "(;GM[1]FF[4]CA[UTF-8]KM[7.5]SZ[" + str(obj['lu']) + "]PB[]PW[]";
    sgf_str += "CP[" + url + "]";

    # 获取题目
    # 101333 = atob("MTAx") + (obj['c']+1)
    r = obj['r'] + 1
    salt = "101" + str(r) + str(r) + str(r)
    result = testcdata(obj['c'], salt)
    json_ret = json.loads(result)

    sgf_str += "\nAB";
    for i in json_ret[0]:
        sgf_str += "[" + i + "]";
    sgf_str += "\nAW";
    for i in json_ret[1]:
        sgf_str += "[" + i + "]";

    sgf_str += '\nC[\n';
    sgf_str += 'title:' + obj['title'] + '\n';
    sgf_str += '\n';
    sgf_str += '黑先' if obj['blackfirst'] else '白先'

    sgf_str += '\n';
    sgf_str += 'qtypename: ' + obj['qtypename'] + '\n';
    sgf_str += 'title: ' + obj['title'] + '\n';
    sgf_str += 'levelname: ' + obj['levelname'] + '\n';
    sgf_str += 'name: ' + (obj['name'] if obj['name'] is not None else 'None') + '\n'
    sgf_str += '\n选项：\n';
    for opt in obj['options']:
        sgf_str += opt['indexname'] + ' ' + opt['content'] + opt['isok'] + '\n';
    sgf_str += ']';

    # 获取解答
    for i in range(len(obj['answers'])):
        an = obj['answers'][i]
        if an['ty'] == 1:
            type_ = '正解'
        elif an['ty'] == 3:
            type_ = '失败'
        elif an['ty'] == 2:
            type_ = '变化'
        elif an['ty'] == 4:
            type_ = '淘汰'
        else:
            type_ = '未知'

        if an['st'] == 2:
            status = '审完'
        elif an['st'] == 1:
            status = '待审'
        else:
            status = '未知'

        pv = '\n('
        prn_pv = 'B ' if obj['blackfirst'] else 'W '
        for j in range(len(obj['answers'][i]['pts'])):
            x = "ABCDEFGHJKLMNOPQRST"['abcdefghijklmnopqrst'.index(obj['answers'][i]['pts'][j]['p'][0])]
            y = 19 - 'abcdefghijklmnopqrst'.index(obj['answers'][i]['pts'][j]['p'][1])
            prn_pv += x + str(y) + ' '
            if obj['blackfirst']:
                pv += ";" + ("B" if j % 2 == 0 else "W") + "[" + obj['answers'][i]['pts'][j]['p'] + "]"
            else:
                pv += ";" + ("W" if j % 2 == 0 else "B") + "[" + obj['answers'][i]['pts'][j]['p'] + "]"
        pv += ')'

        if obj['answers'][i]['ty'] == 1 and obj['answers'][i]['st'] == 2:
            sgf_str += pv

    sgf_str += "\n)"
    return sgf_str

def getq_token(url, token, sessionid):
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh,en;q=0.9,zh-CN;q=0.8',
        'Cache-Control': 'no-cache',
        'DNT': '1',
        'Pragma': 'no-cache',
        'Referer': 'https://www.101weiqi.com/9K/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1'
    }

    cookies = {
        'csrftoken': token,
        'sessionid': sessionid
    }

    # Send the GET request
    response = requests.get(url, headers=headers, cookies=cookies)

    # Print the response text
    print(response.text.find('g_qq'))

if __name__ == '__main__':
    base_url = "https://www.101weiqi.com/"
    level_str = "9K"
    q_str = "4958"
    url = "https://www.101weiqi.com/9K/4958/"
    if len(sys.argv) == 3:
        level_str = sys.argv[1]
        q_str = sys.argv[2]
    url = base_url + level_str + "/" + q_str + "/"
    title = level_str + "-Q-" + q_str
    sgf_name = title + ".sgf"

    # 通过设置登录token和sessionid直接拿
    token = 'ujJhAxo83Z5mg0oRfxtwC2BqgQ0nTjvdeQSBbm3XHqqCWOB9FHF78lqvPA3MF6Ct'
    sessionid = 'gbszfob6tjb67kscg6uytllqskcczewu'
    #get_question(url, token, sessionid)

    # 先登录，然后通过session对象GET
    sess = login()
    resp = getq_sess(url, sess)
    sgf_str = resp_sgf(resp, url)
    with open(sgf_name, 'w') as file:
        file.write(sgf_str)


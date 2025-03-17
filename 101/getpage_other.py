#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import getq
from pymongo import MongoClient, ReturnDocument
import sys

#获取 chizi 和guanzi等, 地址：question/chizi
#获取 9 和13等, 地址：size/9
#集合：4，5，6，7，8，9，11，13，chizi，guanzi，buju，zhongpan，qili，shizhan, pianzhao, shizhan
#{
#  "url_level": "15K+",
#  "url_no": "218455"
#}
#获取clone, 需要单独处理, url类似level，地址：clone/
#但是level代码是数组，希望放入单独的集合，包含url_level和url_no

base_url = "https://www.101weiqi.com/"

header = {
    'cookie':'csrftoken=ujJhAxo83Z5mg0oRfxtwC2BqgQ0nTjvdeQSBbm3XHqqCWOB9FHF78lqvPA3MF6Ct;sessionid=gbszfob6tjb67kscg6uytllqskcczewu',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}
import time
def req_url_retry(url, retry):
    global header
    start_t = time.time()
    ori = retry - 1
    while retry:
        try:
            retry = retry - 1
            #r = requests.get(url, headers=self.header)
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print ("Http Error:",errh)
            continue
        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting:",errc)
            continue
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error:",errt)
            continue
        except requests.exceptions.RequestException as err:
            print ("OOps: Something Else",err)
            continue

        if retry != ori:
            print('retry', ori-retry, 'times', url)
        end_t = time.time()
        print('req_url_retry cost {:5.2f}s'.format(end_t - start_t))
        return 0, r

    end_t = time.time()
    print('req_url_retry cost {:5.2f}s'.format(end_t - start_t))
    return 1, {}

def get_data(base_url, level_str, n):
    client = MongoClient("mongodb://localhost:27017/")  # 连接 MongoDB
    db = client["101"]
    collection = db[level_str]

    url = base_url + prefix + '/' + level_str + "?page=" + str(n)
    ret, resp = req_url_retry(url, 3)
    if ret != 0:
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    if level_str == 'clone':
        divs = soup.find_all('div', class_='wq')
    else:
        divs = soup.find_all('div', class_='col-md-2 col-xs-6 col-sm-3')
    data = []
    for div in divs:
        if level_str == 'clone':
            question_str = '/' + level_str + '/'
            a = div.find('a')
            url_level = 'clone'
            url_no = a['href'][len(question_str):-1]
        else:
            if prefix == '':
                question_str = '/' + level_str + '/'
            else:
                question_str = '/' + prefix + '/'+ level_str + '/'
            a = div.find('a')
            title = a.find('span', class_='warptext').text
            img_url = a.find('img')['src']
            problem_url = base_url + a['href']
            url_level = title.split()[0]
            url_no = a['href'][len(question_str):-1]
        print(url_level, url_no)
        quit()

        existing_doc = collection.find_one({"url_no": url_no})
        if not existing_doc:
            # 如果 url_no 不存在，则插入新文档
            collection.insert_one({"url_level": url_level, "url_no": url_no})
            print(f"new {url_level} {url_no}")
        elif existing_doc["url_level"] != url_level:
            print(f"duplicate {url_no} {url_level}, already {existing_doc.get("url_level")}")
        else:
            print(f"duplicate {url_no} {url_level}, already {existing_doc.get("url_level")}")
        data.append(url_no)
    return data

def get_pagenum_v1(soup):
    ellipsis_element = soup.find('a', text='...')
    ellipsis_parent_element = ellipsis_element.parent
    last_page_parent_element = ellipsis_parent_element.find_next_sibling('li')
    last_page_element = last_page_parent_element.find('a')
    last_page = int(last_page_element.text)
    return last_page

def get_pagenum(soup):
    page_numbers = []
    for a in soup.select('ul.pagination a'):
        if a.text.isdigit():  # 只考虑数字页码
            page_numbers.append(int(a.text))

    if page_numbers:
        last_page = max(page_numbers)  # 取最大页码
    else:
        last_page = 1  # 如果没有找到页码，默认返回 1
    return last_page

def get_content_level(level_str):
    global base_url

    level_url = base_url + prefix +'/' + level_str
    ret, resp = req_url_retry(level_url, 3)
    if ret != 0:
        return None
    soup = BeautifulSoup(resp.text, 'html.parser')
    pagenum = get_pagenum(soup)
    print(level_str, 'total_page', pagenum)

    all_data = []
    for i in range(1, pagenum+1):
        data = get_data(base_url, level_str, i)
        if data == None:
            continue
        all_data.extend(data)

    df = pd.DataFrame(all_data)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_colwidth', None):
        print(df.head())
    print(f'total {len(df.index)}')

if __name__ == '__main__':
    '''
    prefix = 'question'
    level_str = "chizi"
    level_str = "guanzi"
    level_str = "buju"
    level_str = "qili"
    level_str = "zhongpan"
    level_str = "pianzhao"
    level_str = "shizhan"

    prefix = 'size'
    level_str = "13"
    level_str = "9"
    level_str = "4"
    level_str = "5"
    level_str = "11"
    level_str = "8"
    level_str = "6"
    level_str = "7"

    prefix = ''
    level_str = "9K"
    '''

    # clone没去除/，所以拿到url_no都少了第一个字符,已经删除集合
    prefix = ''
    level_str = "clone"
    get_content_level(level_str)

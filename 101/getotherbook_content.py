#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json

# 解析level,question,size,clone的页面

def getotherbook_content_next_pagenum(soup):
    pagination = soup.find('ul', class_='pagination')
    next_page_link = pagination.find('a', string='下一页')

    next_pagenum = 0
    if next_page_link and 'href' in next_page_link.attrs:
        href = next_page_link['href']
        match = re.search(r'page=(\d+)', href)
        #no match: print('下一页 href 没有页面号码：应该是最后页')
        if match:
            next_pagenum = int(match.group(1))
    else:
        print('没有下一页 href：可能只有一页')

    return next_pagenum

#从网页内容提取url_level，url_no，url，返回列表
def getotherbook_content(html_content, path_type, level):
    soup = BeautifulSoup(html_content, 'html.parser')
    next_pagenum = getotherbook_content_next_pagenum(soup)

    data = []
    if path_type == 'clone':
        divs = soup.find_all('div', class_='wq')
    else:
        divs = soup.find_all('div', class_='col-md-2 col-xs-6 col-sm-3')
    for div in divs:
        a_tag = div.find('a', href=True)

        # 得到题目的第一链接，一定是存在的
        href = a_tag['href']
        url_frombook = href

        url_no = ""
        url_level = ""
        span = a_tag.find('span', class_='warptext')
        if span: #clone没有span，level/size/other都有，level的span内容是Q-xxx，size/other是url_level
            if level == "":
                text = span.get_text(strip=True)
                url_level_match = re.match(r'(\S+)', text)
                if url_level_match:
                    url_level = url_level_match.group(1)
            else: # level已经自带url_level，获取url_no
                url_level = level
                text = span.find(string=True, recursive=False).strip()
                url_no_match = re.search(r'Q-(\d+)', text)
                if url_no_match:
                    url_no = url_no_match.group(1)

        if url_no == "": # size/other, 还有clone没有url_no，直接从url里面解
            pattern = r'/{}/(?:[^/]+/)?(\d+)/'.format(path_type)
            match = re.search(pattern, href)
            if match:
                url_no = match.group(1)

        data.append({'url_no': url_no, 'url_level': url_level, 'url_frombook': url_frombook})

    return next_pagenum, data

from pprint import pprint
if __name__ == '__main__':
    #旧网站
    book_list = [
        {'name': 'book/clone_page143.html', 'path_type': 'clone',    'level': ""},
        {'name': 'book/13_page43.html',     'path_type': 'size',     'level': ""},
        {'name': 'book/chizi_page1.html',   'path_type': 'question', 'level': ""},
        {'name': 'book/buju_page66.html',   'path_type': 'question', 'level': ""},
        {'name': 'book/9K_page20.html',     'path_type': 'level',    'level': '9K'}, #先不考虑 level
    ]
    for b in book_list:
        book_complete_htmlname = b.get('name')
        path_type = b.get('path_type')
        level = b.get('level')
        print(book_complete_htmlname, path_type)
        with open(book_complete_htmlname, "r", encoding="utf-8") as file:
            html_content = file.read()
        next_pagenum, ret = getotherbook_content(html_content, path_type, level)
        pprint(ret[0])
        print('下一页', next_pagenum)
        print()


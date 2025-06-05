#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json

# 从cover的content页，获取题目

#从网页内容提取url_level，url_no，url，返回列表
def getotherbook_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract next_pagenum
    pagination = soup.find('ul', class_='pagination')

    next_page_link = pagination.find('a', string='下一页')

    if next_page_link and 'href' in next_page_link.attrs:
        href = next_page_link['href']  # e.g., "?page=2"
        match = re.search(r'page=(\d+)', href)
        if match:
            next_pagenum = int(match.group(1))
            print('next_pagenum:', next_pagenum)
        else:
            next_pagenum = 0
            print('Page number not found in href')
    else:
        next_pagenum = 0
        print('No "下一页" link found')

    # Extract data
    data = []
    divs = soup.find_all('div', class_='col-md-2 col-xs-6 col-sm-3')

    for div in divs:
        a_tag = div.find('a', href=True)
        if not a_tag:
            continue

        href = a_tag['href']
        match = re.search(r'/question/chizi/(\d+)/', href)
        if match:
            url_no = match.group(1)
        else:
            continue

        span = a_tag.find('span', class_='warptext')
        if not span:
            continue

        text = span.get_text(strip=True)
        url_level_match = re.match(r'(\S+)', text)
        if url_level_match:
            url_level = url_level_match.group(1)
        else:
            continue

        data.append({'url_no': url_no, 'url_level': url_level})

    return next_pagenum, data

from pprint import pprint
if __name__ == '__main__':
    #旧网站
    #book_complete_htmlname = 'book/chizi_page1.html'
    book_complete_htmlname = 'book/buju_page66.html'
    with open(book_complete_htmlname, "r", encoding="utf-8") as file:
        html_content = file.read()
    next_pagenum, ret = getotherbook_content(html_content)
    pprint(ret)


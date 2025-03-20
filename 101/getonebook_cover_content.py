#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

# 从cover的content页，获取题目

#从网页内容提取url_level，url_no，url，返回列表
def getonebook_cover_content(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    question_items = soup.find_all('div', class_='questionitem')
    url_contents = []
    for item in question_items:
        # 提取'url_frombook'，即<a>标签的'href'属性
        a_tag = item.find('a')
        if a_tag and 'href' in a_tag.attrs:
            url_frombook = a_tag['href']
        else:
            url_frombook = ''
        
        # 提取'url_no'，查找文本中'Q-'后面的数字
        text_node = item.find(text=re.compile(r'Q-\d+'))
        if text_node:
            match_no = re.search(r'Q-(\d+)', text_node)
            if match_no:
                url_no = match_no.group(1)
            else:
                url_no = ''
        else:
            url_no = ''
        
        # 提取'url_level'，即<span class="pull-right">中的内容
        pattern = r'\b(\d+[DK])\+?.*?Q-(\d+)'
        span = item.find('span', class_='pull-right')
        if span:
            url_level = span.get_text()
            if url_level[-1] == '+':
                url_level = url_level[:-1]
        else:
            url_level = ''
        
        url_contents.append({
            'url_level':    url_level,
            'url_no':       url_no,
            'url_frombook': url_frombook
        })
    return url_contents

from pprint import pprint
if __name__ == '__main__':
    book_complete_htmlname = 'book/62635_cover_121970.html'
    with open(book_complete_htmlname, "r", encoding="utf-8") as file:
        html_content = file.read()
    ret = getonebook_cover_content(html_content)
    pprint(ret)


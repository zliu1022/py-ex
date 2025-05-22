#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import json

# 从cover的content页，获取题目

#从网页内容提取url_level，url_no，url，返回列表
def getonebook_cover_content_onepage(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    next_pagenum = 0
    pattern = r'var\s+nodedata\s*=\s*\{.*?\};'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        g_qq_str = match.group()
        json_str = g_qq_str[15:-1] # 去除开头的 var g_qq =，以及最后的分号
        try:
            obj = json.loads(json_str)
            curpage = obj.get('pagedata').get('page')
            maxpage = obj.get('pagedata').get('maxpage')
            if curpage+1 <= maxpage:
                next_pagenum = curpage+1
        except json.JSONDecodeError:
            print(f'Failed to decode json: {json_str}')
    else:
        print(f'Failed to find g_qq')

    # 找到包含题目信息的 div
    div_timus = soup.find('div', class_='timus card-wrapper')
    if not div_timus:
        print("未找到包含题目信息的 div。")
        exit()

    # 初始化一个列表来存储提取的数据
    data_list = []

    # 在该 div 下找到所有的 'a' 标签
    for a_tag in div_timus.find_all('a', href=True):
        # 提取 'url_frombook'，即 'href' 属性
        url_frombook = a_tag['href'].replace(" ", "")

        # 在 'a' 标签内找到 'div'，类名为 'thumbnail-txt'
        thumbnail_txt_div = a_tag.find('div', class_='thumbnail-txt')
        if not thumbnail_txt_div:
            continue  # 如果未找到，跳过该项

        # 在 'thumbnail-txt' div 内找到所有的 'span' 元素
        spans = thumbnail_txt_div.find_all('span')
        if len(spans) < 2:
            continue  # 如果 'span' 元素不足，跳过该项

        # 第一个 'span' 包含题号，可能有嵌套的 'span'
        span_q_no = spans[0]
        # 获取嵌套的 'span'
        inner_span = span_q_no.find('span')
        if not inner_span:
            continue  # 如果未找到，跳过该项
        url_no = inner_span.text.strip()

        # 第二个 'span' 包含 'url_level'
        url_level = spans[2].text.strip()

        # 将提取的数据添加到列表中
        data_dict = {
            'url_frombook': url_frombook,
            'url_no': url_no,
            'url_level': url_level
        }
        data_list.append(data_dict)

    return next_pagenum, data_list

from pprint import pprint
if __name__ == '__main__':
    #新网站
    book_complete_htmlname = 'book/43441_cover_56114.html'
    #book_complete_htmlname = 'book/48773_cover_71845.html'

    #旧网站
    #book_complete_htmlname = 'book/62635_cover_121970.html'
    with open(book_complete_htmlname, "r", encoding="utf-8") as file:
        html_content = file.read()
    next_pagenum, ret = getonebook_cover_content_onepage(html_content)
    pprint(ret)


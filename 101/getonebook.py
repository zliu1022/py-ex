#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re

# 从难度页获取总页码, level,no
# 通过外部循环可以获取全部页

#从网页内容提取标题，返回book_name
def extract_book_title(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    h3_tag = soup.find('h3')
    if h3_tag:
        small_tag = h3_tag.find('small')
        if small_tag:
            a_tag = small_tag.find('a')
            if a_tag:
                book_name = a_tag.get_text(strip=True)
                return book_name
    return None

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

#从网页内容提取当前页码和下一页页码，返回(cur_pagenum, next_pagenum)
def extract_page_numbers(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    total_pagenum = get_pagenum(soup)

    pagination = soup.find('ul', class_='pagination')
    cur_pagenum = None
    next_pagenum = None
    if pagination:
        # 获取当前页码
        active_li = pagination.find('li', class_='active')
        if active_li and active_li.a:
            cur_pagenum = active_li.a.get_text(strip=True)

        # 查找文本为“下一页”的<a>标签
        next_a = pagination.find('a', string=re.compile('下一页'))
        if next_a:
            next_href = next_a.get('href')
            next_pagenum_match = re.search(r'page=(\d+)', next_href)
            if next_pagenum_match:
                next_pagenum = next_pagenum_match.group(1)
    return total_pagenum, cur_pagenum, next_pagenum

#从网页内容提取url_level，url_no，url，返回列表
def extract_url_contents(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    divs = soup.find_all('div', class_=re.compile(r'col-md-2'))
    url_contents = []
    for div in divs:
        a_tag = div.find('a')
        if a_tag:
            url = a_tag['href']
            span_tag = a_tag.find('span', class_='warptext')
            if span_tag:
                text = span_tag.get_text(strip=True)
                # 提取url_level和url_no
                # (\b\d+[DK]) ➜ 匹配数字+D/K，单词边界。
                # \+?  ➜ 匹配 +，同样是可选的。
                # .*?  ➜ 非贪婪匹配，跳过任意内容，直到遇到 Q-。
                #      ➜ 这里不要求有空格、不要求有 &nbsp;，任意字符都能跳过。
                # Q-(\d+) ➜ 抓编号数字。
                pattern = r'\b(\d+[DK])\+?.*?Q-(\d+)'
                level_no_match = re.match(pattern, text)
                if level_no_match:
                    url_level = level_no_match.group(1)
                    url_no = level_no_match.group(2)
                    url_contents.append({
                        'url_level': url_level,
                        'url_no': url_no,
                        'url_frombook': url
                    })
                else:
                    print('text no match')
                    print(a_tag)
                    print(span_tag)
                    print(text)
                    quit()
            else:
                print('span_tag no match')
                print(div)
                quit()
        else:
            print('a_tag no match')
            quit()

    return url_contents

def getonebook(html_content):
    book_title = extract_book_title(html_content)
    total_pagenum, cur_pagenum, next_pagenum = extract_page_numbers(html_content)

    url_contents = extract_url_contents(html_content)
    return {
        'book_title': book_title,
        'total_pagenum': total_pagenum,
        'cur_pagenum': cur_pagenum,
        'next_pagenum': next_pagenum,
        'url_contents': url_contents
    }

if __name__ == '__main__':
    #book_complete_htmlname = 'book/中级班练习题_按难度.html'
    book_complete_htmlname = 'book/1097_page10.html'
    #book_complete_htmlname = 'book/2762_cover.html'
    book_complete_htmlname = 'book/21744_cover.html'
    with open(book_complete_htmlname, "r", encoding="utf-8") as file:
        html_content = file.read()

    ret = getonebook(html_content)
    if ret:
        print("标题：", ret['book_title'])
        print("当前页：", ret['cur_pagenum'])
        print("下一页：", ret['next_pagenum'])
        print("内容：")
        for content in ret['url_contents']:
            print(content)


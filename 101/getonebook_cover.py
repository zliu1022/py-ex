#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re

#读取book的封面页，获取完整页面url

def getonebook_cover_q(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    divs = soup.find_all('div', class_='col-md-4 col-xs-6')
    data = []
    for div in divs:
        a = div.find('a')
        title = a.find('span', class_='qname').text
        img_url = a.find('img')['src']
        problem_url = a['href']

        match = re.search(r'Q-(\d+).*?', title)
        if match:
            url_no = match.group(1)
        else:
            # title_name为空,url_no藏在problem_url里面
            url_list = problem_url.split('/') # 不放入book_n_q了，后续特殊处理
            url_no = url_list[4]
        data.append({'url_no': url_no, 'url_level': '15K', 'url_frombook': problem_url})
    return data

def getonebook_cover(html_content):
    book_name = ''
    book_qnum = ''
    book_level = ''
    book_donenum = ''
    book_complete_url = ''
    book_content = []

    soup = BeautifulSoup(html_content, 'html.parser')

    div_content = soup.find('div', class_='qis_content')

    # is_share: false
    if div_content is None:
        return None, None

    # 提取book_name
    # book_name位于<div class="qis_content">下的直接文本内容中
    for element in div_content.contents:
        if isinstance(element, str) and element.strip():
            book_name = element.strip()
            break

    # 提取book_qnum, book_level, book_donenum
    p_text_success = div_content.find('p', class_='text-success').get_text(strip=True)
    match = re.search(r'共(\d+)道题目，平均难度：([\w]+)[\s\S]*?做题次数：(\d+)次', p_text_success)
    if match:
        book_qnum = match.group(1)
        book_level = match.group(2)
        book_donenum = match.group(3)

    # 提取book_complete_url
    p_with_url = div_content.find('p', class_='text-success', style='margin-top:5px;')
    if p_with_url:
        a_tag = p_with_url.find('a')
        if a_tag and 'href' in a_tag.attrs:
            book_complete_url = a_tag['href']

    # 提取book_content
    ul_tag = div_content.find('ul')
    if ul_tag:
        li_tags = ul_tag.find_all('li')
        for li in li_tags:
            # 提取content_no
            li_text = li.get_text(strip=True)
            content_no_match = re.match(r'(\d+)、', li_text)
            content_no = content_no_match.group(1) if content_no_match else ''

            # content_url
            a_tag = li.find('a', class_='node')
            content_url = a_tag['href'] if a_tag and 'href' in a_tag.attrs else ''

            # 提取content_name
            a_tag = li.find('a', class_='node')
            content_name = a_tag.get_text() if a_tag else ''
            # 提取content_num
            content_num_match = re.search(r'\((\d+)\)', li.get_text())
            content_num = content_num_match.group(1) if content_num_match else ''
            # 添加到book_content列表
            book_content.append({
                'no':   content_no,
                'url':  content_url,
                'name': content_name,
                'num':  content_num
            })
    else:
        print('Warning: getonebook_cover no content')
    
    doc = {
        'book_name': book_name,
        'book_qnum': book_qnum,
        'book_level': book_level,
        'book_donenum': book_donenum,
        'book_complete_url': book_complete_url,
        'book_content': book_content
    }

    #继续解，level1,30268
    doc_q = getonebook_cover_q(html_content)

    return doc, doc_q

from pprint import pprint
if __name__ == "__main__":
    bookcover_list = [
        #'book/43441_cover.html', # 新网站
        'book/62635_cover.html',
        #"book/中级班练习题.html",
        #'book/21744_cover.html',
        #'book/28238_cover.html',
        #'book/64239_cover_nocomplete.html',
        #'book/52398_cover_emptytitle.html',
        #'book/30268_cover_all.html',
        #'book/64312_cover.html'
    ]
    for b in bookcover_list:
        print(b)
        with open(b, 'r', encoding='utf-8') as f:
            html_content = f.read()
        ret, ret_q = getonebook_cover(html_content)
        pprint(ret)
        pprint(ret_q)
        print(len(ret_q))
        print()


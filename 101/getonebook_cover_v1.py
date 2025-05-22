#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import re
import json

def getonebook_cover_v1(html_content):
    result = {}

    pattern = r'var\s+bookdata\s*=\s*\{.*?\};'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        g_qq_str = match.group()
        json_str = g_qq_str[15:-1] # 去除开头的 var g_qq =，以及最后的分号
        try:
            obj = json.loads(json_str)
            '''
            print(obj.get('id'))
            print(obj.get('username'))
            print(obj.get('name'))
            print(obj.get('desc'))
            print(obj.get('desctext'))
            print(obj.get('nodecount'))
            print(obj.get('chapters')[0])
            '''
            result['id'] = obj.get('id')
            result['username'] = obj.get('username')
            result['name'] = obj.get('name')
            result['desc'] = obj.get('desc')
            result['desctext'] = obj.get('desctext')
            result['nodecount'] = obj.get('nodecount')
            result['chapters'] = obj.get('chapters')
        except json.JSONDecodeError:
            print(f'Failed to decode json: {json_str}')
            return 1, None
    else:
        print(f'Failed to find g_qq')
        return 2, None

    pattern = r'var\s+bookattr\s*=\s*\{.*?\};'
    match = re.search(pattern, html_content, re.DOTALL)
    if match:
        g_qq_str = match.group()
        json_str = g_qq_str[15:-1] # 去除开头的 var g_qq =，以及最后的分号
        try:
            obj = json.loads(json_str)
            '''
            print(obj.get('qcount'))
            print(obj.get('qlevelname'))
            print(obj.get('questionnum'))
            '''
            result['cover'] = {
                'donenum': obj.get('qcount'),
                'level': obj.get('qlevelname'),
                'qnum': obj.get('questionnum')
            }
        except json.JSONDecodeError:
            print(f'Failed to decode json: {json_str}')
            return 3, None
    else:
        print(f'Failed to find g_qq')
        return 4, None

    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract 'book_complete_url'
    book_complete_url_tag = soup.find('a', class_='cursor-p')
    if book_complete_url_tag:
        #result['book_complete_url'] = book_complete_url_tag['href']
        result['cover'].update({ 'complete_url': book_complete_url_tag['href'] })
    else:
        result['book_complete_url'] = None

    # Extract 'book_donenum'
    book_donenum_tag = soup.find('span', attrs={'x-text': lambda x: x and 'getDoworkTimeTrans' in x})
    #print(book_donenum_tag)
    if book_donenum_tag:
        book_donenum_text = book_donenum_tag.get_text()
        book_donenum = re.search(r'\d+', book_donenum_text)
        if book_donenum:
            result['book_donenum'] = book_donenum.group()
        else:
            result['book_donenum'] = None
    else:
        result['book_donenum'] = None

    # Extract 'book_level'
    book_level_tag = soup.find('span', attrs={'x-text': 'bookattr.qlevelname'})
    #print(book_level_tag)
    if book_level_tag:
        result['book_level'] = book_level_tag.get_text().strip()
    else:
        result['book_level'] = None

    # Extract 'book_name'
    book_name_tag = soup.find('div', class_='fs18', attrs={'x-text': 'bookdata.name'})
    #print(book_name_tag)
    if book_name_tag:
        result['book_name'] = book_name_tag.get_text().strip()
    else:
        result['book_name'] = None

    # Extract 'book_qnum'
    book_qnum_tag = soup.find('span', attrs={'x-text': 'bookattr.qcount.toString()'})
    #print(book_qnum_tag)
    if book_qnum_tag:
        result['book_qnum'] = book_qnum_tag.get_text().strip()
    else:
        result['book_qnum'] = None

    book_content = []
    book_id = result['id']
    count = 1
    for ch in result['chapters']:
        book_content.append({
            'url': f'/book/{book_id}/{ch.get('id')}',
            'no': count,
            'name': ch.get('name'),
            'num': ch.get('nodecount')
        })
        subcount = count*10 + 1
        for subch in ch.get('subs'):
            book_content.append({
                'url': f'/book/{book_id}/{subch.get('id')}',
                'no': subcount,
                'name': subch.get('name'),
                'num': subch.get('nodecount')
            })
            subcount += 1
        count += 1
        
    '''
    # Extract 'book_content'
    row_chapters = soup.find_all('div', class_='row-chapter')

    for chapter in row_chapters:
        chapter_info = {}
        a_tag = chapter.find('a', class_='row-chapter-a flex1')
        if a_tag:
            chapter_info['url'] = a_tag['href']
            max_width_div = a_tag.find('div', class_='max--width85')
            if max_width_div:
                spans = max_width_div.find_all('span')
                if len(spans) >= 2:
                    no_text = spans[0].get_text()
                    name_text = spans[1].get_text()
                    no_match = re.search(r'\d+', no_text)
                    if no_match:
                        chapter_info['no'] = no_match.group()
                    else:
                        chapter_info['no'] = None
                    chapter_info['name'] = name_text.strip()
                else:
                    chapter_info['no'] = None
                    chapter_info['name'] = None
        else:
            chapter_info['url'] = None
            chapter_info['no'] = None
            chapter_info['name'] = None

        num_div = chapter.find('div', attrs={'x-text': lambda x: x and 'getQuestionCountTrans' in x})
        if num_div:
            num_text = num_div.get_text()
            num_match = re.search(r'\d+', num_text)
            if num_match:
                chapter_info['num'] = num_match.group()
            else:
                chapter_info['num'] = None
        else:
            chapter_info['num'] = None

        book_content.append(chapter_info)
    '''
    result['cover'].update({ 'content': book_content})

    # Print the result
    #print(json.dumps(result, ensure_ascii=False, indent=4))

    return 0, result

from pprint import pprint
if __name__ == "__main__":
    bookcover_list = [
        #'book/43441_cover.html', # 新网站
        'book/41950_cover.html',
    ]
    for b in bookcover_list:
        print(b)
        with open(b, 'r', encoding='utf-8') as f:
            html_content = f.read()
        ret, ret_q = getonebook_cover_v1(html_content)
        pprint(ret)
        pprint(ret_q)
        print(len(ret_q))
        print()


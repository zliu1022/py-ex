#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from pypinyin import lazy_pinyin

def find_idioms_with_character(char):
    # 打开idiom.json文件并加载数据
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    # 筛选包含指定字符的成语
    idioms_with_char = [idiom['word'] for idiom in idioms if char in idiom['word']]
    return idioms_with_char

def idiom_include(char):
    """查找包含指定字符的成语"""
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = [idiom['word'] for idiom in idioms if char in idiom['word']]
    return result

def idiom_begin(char):
    """查找以指定字符开头的成语"""
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = [idiom['word'] for idiom in idioms if idiom['word'].startswith(char)]
    return result

def idiom_end(char):
    """查找以指定字符结尾的成语"""
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = [idiom['word'] for idiom in idioms if idiom['word'].endswith(char)]
    return result

def idiom_include_py(char):
    """查找包含与指定字符拼音相同的字的成语"""
    input_pinyin = lazy_pinyin(char)[0]
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = []
    for idiom in idioms:
        for c in idiom['word']:
            if lazy_pinyin(c)[0] == input_pinyin:
                result.append(idiom['word'])
                break  # 发现包含该拼音的字，跳出循环
    return result

def idiom_begin_py(char):
    """查找开头字的拼音与指定字符相同的成语"""
    input_pinyin = lazy_pinyin(char)[0]
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = [idiom['word'] for idiom in idioms if lazy_pinyin(idiom['word'][0])[0] == input_pinyin]
    return result

def idiom_end_py(char):
    """查找结尾字的拼音与指定字符相同的成语"""
    input_pinyin = lazy_pinyin(char)[0]
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = [idiom['word'] for idiom in idioms if lazy_pinyin(idiom['word'][-1])[0] == input_pinyin]
    return result

def print_split_column(ret):
    # 输出包含指定字符的成语
    for i,idiom in enumerate(ret):
        print(idiom, end=' ')
        if (i+1) % 10 == 0:
            print()
    if (i+1) % 10 != 0:
        print()
    print('----------')

def get_pattern(word):
    """获取成语的字母模式，如'AABC'等"""
    mapping = {}
    next_char = 'A'
    pattern = ''
    for ch in word:
        if ch in mapping:
            pattern += mapping[ch]
        else:
            mapping[ch] = next_char
            pattern += next_char
            next_char = chr(ord(next_char) + 1)
    return pattern

def idiom_pattern(pattern):
    """查找符合指定结构模式的成语"""
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = [idiom['word'] for idiom in idioms if get_pattern(idiom['word']) == pattern]
    return result

def idiom_search(char=None, pattern=None):
    """
    组合查找：查找既包含指定字符，又符合指定模式的成语
    :param char: 指定的字符（可选）
    :param pattern: 指定的模式（可选）
    :return: 成语列表
    """
    with open('idiom.json', 'r', encoding='utf-8') as f:
        idioms = json.load(f)
    result = []
    for idiom in idioms:
        word = idiom['word']
        if char and char not in word:
            continue
        if pattern and get_pattern(word) != pattern:
            continue
        result.append(word)
    return result

if __name__ == '__main__':
    if len(sys.argv) == 3:
        char = sys.argv[1]
        pattern = sys.argv[2]
    else:
        char = '龙'  # 要查找的字符
        pattern = 'ABAC'

    '''
    ret = idiom_include(char)
    print_split_column(ret)

    ret = idiom_begin(char)
    print_split_column(ret)

    ret = idiom_end(char)
    print_split_column(ret)

    ret = idiom_include_py(char)
    print_split_column(ret)

    ret = idiom_begin_py(char)
    print_split_column(ret)

    ret = idiom_end_py(char)
    print_split_column(ret)

    # 参考：https://mp.weixin.qq.com/s?__biz=MzI0NDM0ODMwNQ==&mid=2247489619&idx=4&sn=351f58bd64e2815d7e84614394eab22c&chksm=e95e7cadde29f5bbc9d7d4d7a67663d1239bab0e6ca46a287f325ba2289aa5e4d3d0f0b93558&scene=27
    print("符合模式‘{}’的成语：".format(pattern))
    print_split_column(idiom_pattern(pattern))
    '''

    print("包含字符‘{}’且符合模式‘{}’的成语：".format(char, pattern))
    print_split_column(idiom_search(char=char, pattern=pattern))


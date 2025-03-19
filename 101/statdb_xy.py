#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import sys

# 获取q库中的题目prepos的x，y范围，answer的x，y范围
# 并检查answer的xy，是否在prepos的范围+2之内

# 建立MongoDB连接
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["101"]
collection = db["q"]

# 定义字母到数字的映射，跳过字母 'i'
letters = [chr(i) for i in range(ord('a'), ord('s')+1)]
letter_to_num = {letter: index for index, letter in enumerate(letters)}

# 定义一个函数来将棋盘位置字符串转换为 (x, y) 坐标
def position_to_coords(pos_str):
    if len(pos_str) != 2:
        raise ValueError(f"Invalid position string: {pos_str}")
    x_char, y_char = pos_str[0], pos_str[1]
    x = letter_to_num.get(x_char)
    y = letter_to_num.get(y_char)
    if x is None or y is None:
        raise ValueError(f"Invalid position characters: {pos_str}")
    return x, y

BOARD_SIZE = 19

def chk_inside(pre, ans, d):
    if pre['min_x'] - d <= ans['min_x'] and\
        pre['max_x'] + d >= ans['max_x'] and\
        pre['min_y'] - d <= ans['min_y'] and\
        pre['max_y'] + d >= ans['max_y']:
        return 0
    else:
        return 1

def statdb_q(doc):
    # 处理 prepos 字段
    pre = {
        'min_x':BOARD_SIZE,
        'min_y':BOARD_SIZE,
        'max_x':-1,
        'max_y':-1
    }
    prepos = doc.get('prepos', {})
    for color in ['b', 'w']:
        positions = prepos.get(color, [])
        for pos_str in positions:
            try:
                x, y = position_to_coords(pos_str)
                pre['max_x'] = max(pre['max_x'], x)
                pre['max_y'] = max(pre['max_y'], y)
                pre['min_x'] = min(pre['min_x'], x)
                pre['min_y'] = min(pre['min_y'], y)
            except ValueError as e:
                print(e)
    print(f"Prepos X: {pre['min_x']}-{pre['max_x']}, Y: {pre['min_y']}-{pre['max_y']}", end=' ')

    ans = {
        'min_x':BOARD_SIZE,
        'min_y':BOARD_SIZE,
        'max_x':-1,
        'max_y':-1
    }
    # 处理 answers 字段
    answers = doc.get('answers', [])
    for idx, answer in enumerate(answers):
        if answer.get('ty') == 1 and answer.get('st') == 2:
            positions = answer.get('p', [])
            for pos_str in positions:
                try:
                    x, y = position_to_coords(pos_str)
                    ans['max_x'] = max(ans['max_x'], x)
                    ans['max_y'] = max(ans['max_y'], y)
                    ans['min_x'] = min(ans['min_x'], x)
                    ans['min_y'] = min(ans['min_y'], y)
                except ValueError as e:
                    print(e)
    print(f"Answer X: {ans['min_x']}-{ans['max_x']}, Y: {ans['min_y']}-{ans['max_y']}", end=' ')

    if chk_inside(pre, ans, 1) == 0:
        print('OK')
    else:
        print('ERR')

if __name__ == "__main__":
    if len(sys.argv) == 2:
        no = sys.argv[1]
        p = list(collection.find({"url_no": no}))
    else:
        p = collection.find()

    for doc in p:
        print(f"no {doc.get('no')}, r {doc.get('r')}", end=' ')
        statdb_q(doc)


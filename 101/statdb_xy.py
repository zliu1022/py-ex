#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
from config import db_name

# 获取q库中的题目prepos的x，y范围，answer的x，y范围
# 并检查answer的xy，是否在prepos的范围+2之内


# 定义字母到数字的映射，跳过字母 'i'
letters = [chr(i) for i in range(ord('a'), ord('s')+1)]
letter_to_num = {letter: index for index, letter in enumerate(letters)}

BOARD_SIZE = 19

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

def chk_inside(pre, ans, d):
    if pre['min_x'] - d <= ans['min_x'] and\
        pre['max_x'] + d >= ans['max_x'] and\
        pre['min_y'] - d <= ans['min_y'] and\
        pre['max_y'] + d >= ans['max_y']:
        return 0
    else:
        return 1

def statdb_q_xy(doc):
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

def statdb_q():
    # 建立MongoDB连接
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    collection = db["q"]
    p = collection.find()

    for doc in p:
        print(f"no {doc.get('no')}, r {doc.get('r')}", end=' ')
        statdb_q_xy(doc)

def statdb_xy_range():
    # Connect to the MongoDB server (update the URI as needed)
    client = MongoClient('mongodb://localhost:27017/')  # Adjust host and port if necessary

    # Access the database and collection
    db = client[db_name]  # Use your database name
    collection = db['q']  # Use your collection name

    # Initialize lists to store x and y values
    x_values = []
    y_values = []

    x_range= []
    y_range= []
    # Iterate through all documents in the collection
    criteria = {'status':2, 'qtype':'死活题', 'size':19}
    for doc in collection.find(criteria):
        x_list = []
        y_list = []
        min_pp_str = doc.get('min_pp', '')
        if min_pp_str:
            try:
                # Parse the string to a list of lists
                min_pp = json.loads(min_pp_str)

                # Iterate through each coordinate in min_pp
                for entry in min_pp:
                    if len(entry) == 3:
                        color = entry[0]  # 'b' or 'w'
                        x = entry[1]
                        y = entry[2]
                        # Ensure x and y are integers
                        if isinstance(x, int) and isinstance(y, int):
                            if x<0 or x>19 or y<0 or y>19:
                                continue
                            x_values.append(x)
                            y_values.append(y)
                            x_list.append(x)
                            y_list.append(y)
                        else:
                            print(f"Invalid coordinate types in {entry}")
                    else:
                        print(f"Unexpected format in {entry}")

                x_min = min(x_list)
                x_max = max(x_list)
                y_min = min(y_list)
                y_max = max(y_list)
                x_range.append(x_max-x_min+1)
                y_range.append(y_max-y_min+1)
            except json.JSONDecodeError as e:
                print(f"JSON decode error in document {doc['_id']}: {e}")
        else:
            print(f"No 'min_pp' field in document {doc['_id']}")

    print(criteria)
    # Calculate min and max for x and y
    min_x = min(x_values)
    max_x = max(x_values)
    min_y = min(y_values)
    max_y = max(y_values)
    print(f"x ranges: {min_x} {max_x} y ranges: {min_y} {max_y}")
    min_x = min(x_range)
    max_x = max(x_range)
    min_y = min(y_range)
    max_y = max(y_range)
    print(f"x-x ranges: {min_x} {max_x} y-y ranges: {min_y} {max_y}")
    draw_distribution_xy_range(x_range, y_range)

def draw_distribution_xy_range(x, y):
    # Count the occurrences of each integer value in x and y, ensuring the range covers 0 to 18
    counts_x = np.bincount(x, minlength=21)
    counts_y = np.bincount(y, minlength=21)

    # Create an array of integer values from 0 to 18
    bins = np.arange(21)

    # Print counts for each integer value
    print("Counts for each integer value:")
    for i in bins:
        print(f"Integer Value: {i}, Counts: x={counts_x[i]}, y={counts_y[i]}")

    # Calculate cumulative counts
    cum_counts_x = np.cumsum(counts_x)
    cum_counts_y = np.cumsum(counts_y)

    # Calculate cumulative percentages
    total_counts_x = counts_x.sum()
    total_counts_y = counts_y.sum()
    cum_percent_x = cum_counts_x / total_counts_x * 100
    cum_percent_y = cum_counts_y / total_counts_y * 100

    # Print cumulative percentages for each integer value
    print("\nCumulative percentages up to each integer value:")
    for i in bins:
        print(f"Integer Value: {i}, Cumulative Percentage <= {i}: x={cum_percent_x[i]:.2f}%, y={cum_percent_y[i]:.2f}%")

    # Set the width of each bar
    bar_width = 0.4

    # Calculate the positions for the bars
    positions_x = bins - bar_width / 2
    positions_y = bins + bar_width / 2

    # Create a figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot the counts for arrays x and y in the left subplot
    ax1.bar(positions_x, counts_x, width=bar_width, color='blue', edgecolor='black', label='Array x')
    ax1.bar(positions_y, counts_y, width=bar_width, color='red', edgecolor='black', label='Array y')

    # Set title and labels for the left subplot
    ax1.set_title('Distribution of Integer Occurrences', fontsize=14)
    ax1.set_xlabel('Integer Value', fontsize=12)
    ax1.set_ylabel('Occurrence Count', fontsize=12)
    ax1.set_xticks(bins)
    ax1.legend()
    ax1.grid(axis='y', linestyle='--', alpha=0.7)

    # Plot the cumulative percentages for arrays x and y in the right subplot
    ax2.plot(bins, cum_percent_x, marker='o', color='blue', label='Array x')
    ax2.plot(bins, cum_percent_y, marker='s', color='red', label='Array y')

    # Set title and labels for the right subplot
    ax2.set_title('Cumulative Percentage Distribution', fontsize=14)
    ax2.set_xlabel('Integer Value', fontsize=12)
    ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12)
    ax2.set_xticks(bins)
    ax2.set_yticks(np.arange(0, 110, 10))  # Set y-axis ticks from 0% to 100%
    ax2.set_ylim(0, 100)  # Ensure y-axis limits from 0% to 100%
    ax2.legend()
    ax2.grid(True, linestyle='--', alpha=0.7)

    # Adjust layout to prevent overlapping
    plt.tight_layout()

    # Display the plots
    plt.show()

if __name__ == "__main__":
    statdb_xy_range()


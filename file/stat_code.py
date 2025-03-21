#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def count_lines_in_file(file_path):
    """统计单个文件的代码行、注释行和空行数"""
    code_lines = 0
    comment_lines = 0
    empty_lines = 0
    in_multiline_comment = False

    with open(file_path, 'r', encoding='utf-8') as fp:
        for line in fp:
            stripped_line = line.strip()
            if not stripped_line:  # 空行
                empty_lines += 1
            elif in_multiline_comment:  # 多行注释
                comment_lines += 1
                if stripped_line.endswith("'''") or stripped_line.endswith('"""'):
                    in_multiline_comment = False
            elif stripped_line.startswith('#'):  # 单行注释
                comment_lines += 1
            elif stripped_line.startswith("'''") or stripped_line.startswith('"""'):  # 开始多行注释
                comment_lines += 1
                in_multiline_comment = True
                if stripped_line.endswith("'''") or stripped_line.endswith('"""'):
                    in_multiline_comment = False
            else:  # 有效代码行
                code_lines += 1

    return code_lines, comment_lines, empty_lines

def print_markdown_table(file_stats):
    """打印Markdown格式的表格"""
    print("| 文件名          | 代码行 | 注释行 | 空行 |")
    print("|------------------|--------|--------|------|")
    for file_stat in file_stats:
        print(f"| {file_stat['name']:15s} | {file_stat['code']:6d} | {file_stat['comment']:6d} | {file_stat['empty']:4d} |")
    print("|------------------|--------|--------|------|")

    total_code = sum(stat['code'] for stat in file_stats)
    total_comment = sum(stat['comment'] for stat in file_stats)
    total_empty = sum(stat['empty'] for stat in file_stats)

    print(f"| 总计            | {total_code:6d} | {total_comment:6d} | {total_empty:4d} |")

def code_lines_count(path):
    """统计整个目录及子目录中所有Python文件的代码行数、注释行数和空行数"""
    file_stats = []

    for root, dirs, files in os.walk(path):
        for item in files:
            if item.endswith('.py'):  # 只统计.py文件
                file_abs_path = os.path.join(root, item)
                code, comment, empty = count_lines_in_file(file_abs_path)
                file_stats.append({
                    'name': item,
                    'code': code,
                    'comment': comment,
                    'empty': empty
                })

    print_markdown_table(file_stats)
    return file_stats

if __name__ == '__main__':
    abs_dir = os.getcwd()
    code_lines_count(abs_dir)


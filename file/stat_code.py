#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

def code_lines_count(path):
    code_lines = 0
    comm_lines = 0
    space_lines = 0

    for root, dirs, files in os.walk(path):
        for item in files:
            file_abs_path = os.path.join(root, item)
            postfix = os.path.splitext(file_abs_path)[1]
            if postfix != '.py':
                continue

            # 按文件处理
            cur_comm = 0
            cur_code = 0
            cur_empty = 0
            in_multiline_comment = False

            with open(file_abs_path, 'r', encoding='utf-8') as fp:
                for line in fp:
                    stripped_line = line.strip()
                    if not stripped_line:  # 空行
                        space_lines += 1
                        cur_empty += 1
                    elif in_multiline_comment:  # 多行注释
                        comm_lines += 1
                        cur_comm += 1
                        if stripped_line.endswith("'''") or stripped_line.endswith('"""'):
                            in_multiline_comment = False
                    elif stripped_line.startswith('#'):  # 单行注释
                        comm_lines += 1
                        cur_comm += 1
                    elif stripped_line.startswith("'''") or stripped_line.startswith('"""'):  # 开始多行注释
                        comm_lines += 1
                        cur_comm += 1
                        in_multiline_comment = True
                        if stripped_line.endswith("'''") or stripped_line.endswith('"""'):
                            in_multiline_comment = False
                    else:  # 有效代码行
                        code_lines += 1
                        cur_code += 1

            print(f'{item:15s} code {cur_code:4d} comm {cur_comm:4d} empty {cur_empty:4d}')

    print(f'total           code {code_lines:4d} comm {comm_lines:4d} empty {space_lines:4d}')
    return code_lines, comm_lines, space_lines

if __name__ == '__main__':
    abs_dir = os.getcwd()
    x, y, z = code_lines_count(abs_dir)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 从html解出title

import re
import os

#with open('.cache/4958.html', 'r', encoding='utf-8') as f:
#with open('.cache/179111.html', 'r', encoding='utf-8') as f:

def extract_title_info(html):
    pattern = r"<title>\s*Q-(\d+)\s*-\s*(\S+?)\s*-"
    match = re.search(pattern, html, re.S)
    if match:
        return match.group(1), match.group(2)
    return None, None

def process_html_files(directory):
    """ 遍历指定目录下的所有 .html 文件，并提取 title_id 和 title_level """
    for filename in os.listdir(directory):
        if filename.endswith(".html"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as file:
                html_content = file.read()
                title_id, title_level = extract_title_info(html_content)

                if title_id and title_level:
                    print(f"{filename} {title_id} {title_level}")
                else:
                    print(f"{filename} 匹配失败")

# 运行函数，处理 .cache 目录
cache_directory = ".cache"
process_html_files(cache_directory)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys

def count_and_sample_characters(text, num_samples=10):
    chinese_count = 0
    english_word_count = 0
    other_symbol_count = 0

    '''
    chinese_samples = []
    english_word_samples = []
    other_symbol_samples = []
    '''

    chinese_samples = set()
    english_word_samples = set()
    other_symbol_samples = set()

    current_english_word = ""

    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            chinese_count += 1
            if len(chinese_samples) < num_samples:
                #chinese_samples.append(char)
                chinese_samples.add(char)
        elif char.isalpha():
            current_english_word += char
        else:
            if current_english_word:
                english_word_count += 1
                if len(english_word_samples) < num_samples and current_english_word not in english_word_samples:
                    #english_word_samples.append(current_english_word)
                    english_word_samples.add(current_english_word)
                current_english_word = ""
            if not char.isspace():
                other_symbol_count += 1
                if len(other_symbol_samples) < num_samples and char not in other_symbol_samples:
                    #other_symbol_samples.append(char)
                    other_symbol_samples.add(char)

    # Check if there's an English word pending to be counted
    if current_english_word:
        english_word_count += 1
        if len(english_word_samples) < num_samples and current_english_word not in english_word_samples:
            english_word_samples.append(current_english_word)

    return {
        "chinese_count": chinese_count, "chinese_samples": chinese_samples,
        "english_word_count": english_word_count, "english_word_samples": english_word_samples,
        "other_symbol_count": other_symbol_count, "other_symbol_samples": other_symbol_samples
    }

import chardet

def open_text_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read(4096)  # 读取文件的前4096字节来猜测编码
            encoding = chardet.detect(raw_data)['encoding']
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return
    print('encoding', encoding)

    try:
        with open(file_path, 'r', encoding=encoding) as file:
            return file.read()
    except UnicodeDecodeError as e:
        print(f"读取文件时发生编码错误：{e}")
        return None

def process_text_file(filename="sophie_world.txt", sample_num=10):
    text_content = open_text_file(filename)
    if text_content is None:
        return

    result = count_and_sample_characters(text_content, sample_num)

    #print(json.dumps(result, indent=4))

    sorted_ch_sample = sorted(result['chinese_samples'])
    sorted_en_sample = sorted(result['english_word_samples'])
    sorted_other_sample = sorted(result['other_symbol_samples'])
    print('ch_char:  ', result['chinese_count'], sorted_ch_sample)
    print('en_word:  ', result['english_word_count'], sorted_en_sample)
    print('other:    ', result['other_symbol_count'], sorted_other_sample)

if __name__ == "__main__":
    filename = "sophie_world.txt"
    #file_path = 'hekaiming_medium.txt'
    sample_num = 10

    if len(sys.argv) > 1:
        filename = sys.argv[1]
    if len(sys.argv) > 2:
        sample_num = int(sys.argv[2])

    process_text_file(filename, sample_num)

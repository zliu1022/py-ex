#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    encoding = result['encoding']
    confidence = result['confidence']
    print(f"检测到的编码: {encoding} (置信度: {confidence*100:.2f}%)")
    return encoding

def convert_encoding(input_path, output_path, target_encoding='utf-8'):
    original_encoding = detect_encoding(input_path)
    if original_encoding is None:
        print("无法检测文件编码。请手动指定编码。")
        return

    try:
        with open(input_path, 'r', encoding=original_encoding, errors='replace') as f:
            content = f.read()
        with open(output_path, 'w', encoding=target_encoding) as f:
            f.write(content)
        print(f"文件已成功转换为 {target_encoding} 编码，保存为 {output_path}")
    except Exception as e:
        print(f"转换过程中发生错误: {e}")

if __name__ == "__main__":
    input_file = 'sgz.txt'    # 替换为您的乱码文件路径
    output_file = 'fixed.txt'     # 您希望保存的转换后文件路径
    convert_encoding(input_file, output_file)


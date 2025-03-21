#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
from bs4 import BeautifulSoup
import zipfile
import shutil

# 定义要抓取的网页URL
url = 'https://katagoarchive.org/g104/models/index.html'
base_url = 'https://katagoarchive.org/g104/models/'

# 发送HTTP请求获取网页内容
response = requests.get(url)
response.raise_for_status()  # 如果请求失败，抛出异常

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 找到所有链接
links = soup.find_all('a')

# 定义下载目录
download_dir = 'downloads'
os.makedirs(download_dir, exist_ok=True)

# 遍历所有链接并下载文件
for no, link in enumerate(links):
    file_url = base_url + link.get('href')
    file_name = os.path.join(download_dir, link.get('href').split('/')[-1])

    f_name = link.get('href').split('/')[-1]
    if f_name == "index.html": continue
    if no <= 11: continue
    
    # 发送HTTP请求下载文件
    file_response = requests.get(file_url)
    file_response.raise_for_status()  # 如果请求失败，抛出异常
    
    # 将文件内容写入本地文件
    with open(file_name, 'wb') as file:
        file.write(file_response.content)
    
    print(f'{no} Downloaded {file_name}')

    # 解压zip文件
    with zipfile.ZipFile(file_name, 'r') as zip_ref:
        zip_ref.extractall(download_dir)

    # 找到并重命名model.txt.gz文件
    extracted_dir = file_name.replace('.zip', '')
    model_txt_gz_path = os.path.join(extracted_dir, 'model.txt.gz')
    new_gz_name = file_name.replace('.zip', '.gz')

    if os.path.exists(model_txt_gz_path):
        os.rename(model_txt_gz_path, new_gz_name)
        #print(f'Renamed {model_txt_gz_path} to {new_gz_name}')

        # 删除解压后的目录
        shutil.rmtree(extracted_dir)
        #print(f'Deleted directory {extracted_dir}')
        
        # 删除zip文件
        os.remove(file_name)
        #print(f'Deleted zip file {file_name}')
    else:
        print(f'Error: {model_txt_gz_path} does not exist')
    print()

    if no == 20: break

print('All files downloaded.')


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import requests
from urllib.parse import urlparse, unquote
from PIL import Image

# 把md文件中，是url的image下载到本地，并压缩，替换成本地文件

# 设置参数
markdown_file = "local.md"  # 替换为你的 Obsidian 文章路径
output_dir = "ori_images"  # 存放原始图片的目录
compressed_dir = "images"  # 存放压缩图片的目录
scale_factor = 0.6  # 压缩比例

# 确保存放目录存在
os.makedirs(output_dir, exist_ok=True)
os.makedirs(compressed_dir, exist_ok=True)

# 读取 Markdown 文件内容
with open(markdown_file, "r", encoding="utf-8") as f:
    content = f.read()

# 查找所有图片 URL
image_pattern = r"!\[\]\((https?://[^\)]+)\)"
matches = re.findall(image_pattern, content)

# 下载图片并处理
for url in matches:
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            # 解析 URL 获取原始文件名
            parsed_url = urlparse(url)
            original_filename = os.path.basename(unquote(parsed_url.path))  # 解码 URL 以恢复原始文件名
            original_filename = os.path.splitext(original_filename)[0] + ".jpg"  # 统一扩展名为 .jpg

            local_path = os.path.join(output_dir, original_filename)

            # 避免重名文件覆盖
            base_name = os.path.splitext(original_filename)[0]
            compressed_filename = f"{base_name}.jpg"
            compressed_path = os.path.join(compressed_dir, compressed_filename)

            # 保存原始图片
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)

            # 压缩图片
            with Image.open(local_path) as img:
                new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
                img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
                img_resized.save(compressed_path, quality=85)

            # 修改 Markdown 文件中的图片引用
            local_md_path = compressed_path.replace("\\", "/")
            content = content.replace(f"![]({url})", f"![]({local_md_path})")

            print(f"下载并压缩成功: {url} -> {compressed_path} ({new_size[0]}x{new_size[1]})")
        else:
            print(f"下载失败: {url}")

    except Exception as e:
        print(f"处理 {url} 失败: {e}")

# 写回 Markdown 文件
with open(markdown_file, "w", encoding="utf-8") as f:
    f.write(content)

print("所有图片处理完成！")


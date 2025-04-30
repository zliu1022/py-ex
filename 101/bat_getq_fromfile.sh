#!/bin/bash

mv ~/Downloads/q_*.html ~/Downloads/q/

# 遍历 ~/Downloads/q 目录下的所有 .html 文件
for file in ~/Downloads/q/q_*.html; do
    # 检查文件是否存在，防止目录中没有 .html 文件的情况
    if [[ -f "$file" ]]; then
        echo "Processing $file"
        # 调用 getq_fromfile.py 脚本并传递文件名作为参数
        ./getq_fromfile.py "$file"
    else
        echo "No q_HTML files found in ~/Downloads/q"
    fi
done

mv ~/Downloads/q/q_*.html ~/Downloads/q/done

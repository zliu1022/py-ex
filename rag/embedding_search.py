#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lancedb.pydantic import LanceModel, Vector
import numpy as np
import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd

file_name = 'jane'
query = "According to the original novel of 'Jane Eyre', did Jane and Rochester have children at the end? What exactly happened? Please quote the original text to explain."
#file_name = 'sgz'
#query = '典韦'

# 1. 加载 Jina 中英双语嵌入模型
embedder = SentenceTransformer('./jina-embeddings-v2-base-zh', trust_remote_code=True)
embedder.max_seq_length = 2048

# 2. 连接到本地 LanceDB 数据库（目录）
# 3. 打开已存在的表（假设已用相同表名写入过数据）
db = lancedb.connect('./lancedb')
#file_name = 'jane'

query_emb = embedder.encode([query])[0].astype(np.float32)

def print_ret(ret):
    for idx, row in enumerate(ret):
        text = row['text']
        score = row['_distance'] if '_distance' in row else row['_score']
        print(f"{idx+1:03d} {score:.4f} {text[:150]}{'...' if len(text)>150 else ''}")

chunk_sizes = [0, 1, 2, 5, 10]
chunk_sizes = [0]
for chunk_size in chunk_sizes:
    if chunk_size == 0:
        table_name = file_name
    else:
        table_name = file_name+str(chunk_size)
    table = db.open_table(table_name)

    total_records = table.count_rows()
    print(f"{chunk_size} 总记录数：{total_records}，开始搜索并打印所有匹配结果……")

    limit_num = 5
    results = table.search(query_emb, vector_column_name="embedding").bypass_vector_index().limit(limit_num).to_list()
    results_sorted = sorted(results, key=lambda r: r["_distance"])
    print_ret(results_sorted)
    print()


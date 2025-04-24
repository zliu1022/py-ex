#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lancedb.pydantic import LanceModel, Vector
import numpy as np
import lancedb
from sentence_transformers import SentenceTransformer
import pandas as pd

#file_name = 'jane'
#query = 'Jane and Rochester\'s child'
file_name = 'sgz'
query = '典韦'

# 1. 加载 Jina 中英双语嵌入模型
embedder = SentenceTransformer('jinaai/jina-embeddings-v2-base-zh', trust_remote_code=True)
embedder.max_seq_length = 2048

# 2. 连接到本地 LanceDB 数据库（目录）
# 3. 打开已存在的表（假设已用相同表名写入过数据）
db = lancedb.connect('./lancedb')
#file_name = 'jane'
table = db.open_table(file_name)

query_emb = embedder.encode([query])[0].astype(np.float32)

total_records = table.count_rows()
print(f"总记录数：{total_records}，开始搜索并打印所有匹配结果……")

#results = table.search(query_emb.tolist()).to_list()
results = table.search(query_emb, vector_column_name="embedding").bypass_vector_index().limit(12).to_list()
results_sorted = sorted(results, key=lambda r: r["_distance"])

for idx, row in enumerate(results_sorted):
    text = row['text']
    score = row['_distance'] if '_distance' in row else row['_score']
    print(f"{idx+1:03d}. 距离 {score:.4f} → {text[:100]}{'...' if len(text)>100 else ''}")


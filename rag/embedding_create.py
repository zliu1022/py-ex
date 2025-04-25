#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lancedb.pydantic import LanceModel, Vector
import numpy as np
import lancedb
from sentence_transformers import SentenceTransformer
import re

class Entry(LanceModel):
    text: str
    embedding: Vector(768)

def insert(db, table_name, docs):
    embs = embedder.encode(docs, show_progress_bar=True)
    embs = np.array(embs, dtype=np.float32)

    # 删除已存在的表（如果存在）
    if table_name in db.table_names():
        db.drop_table(table_name)

    table = db.create_table(
        name=table_name,
        schema=Entry,
        mode='overwrite'
    )

    # 将数据写入，LanceDB 会根据模型校验并转换类型
    records = [
        Entry(text=text, embedding=emb.tolist())
        for text, emb in zip(docs, embs)
    ]
    table.add(records)

    table.create_index(
        vector_column_name='embedding',
        num_partitions=128,
        num_sub_vectors=64
    )

def chinese_sentence_tokenizer(text): # 自定义的中文分句函数
    return re.split(r'(?<=[。！？])', text)

#file_name = 'sgz'
file_name = 'jane'
embedder = SentenceTransformer('./jina-embeddings-v2-base-zh', trust_remote_code=True)
db = lancedb.connect('./lancedb')

# 按行分割读取
docs = [line.strip() for line in open(file_name + '.txt', encoding='utf-8') if line.strip()]
table_name = file_name
if table_name not in db.table_names():
    insert(db, table_name, docs)

quit()

# 多行读取, 合并固定数量的句子为一个文本块
with open(file_name + '.txt', 'r', encoding='utf-8') as f:
    text_data = f.read()
sentences = chinese_sentence_tokenizer(text_data)
sentences = [s.strip() for s in sentences if s.strip()]
chunk_sizes = [1, 2, 5, 10]
for chunk_size in chunk_sizes:
    docs = [''.join(sentences[i:i+chunk_size]) for i in range(0, len(sentences), chunk_size)]
    print(f"正在处理 chunk_size = {chunk_size}，文本块数量：{len(docs)}")
    table_name = file_name + str(chunk_size)
    if table_name in db.table_names():
        continue

    insert(db, table_name, docs)
    print(f"chunk_size = {chunk_size} 的表已创建，表名为 {table_name}\n")


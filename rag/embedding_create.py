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

file_name = 'sgz'

embedder = SentenceTransformer('jinaai/jina-embeddings-v2-base-zh', trust_remote_code=True)

docs = [line.strip() for line in open(file_name + '.txt', encoding='utf-8') if line.strip()]

embs = embedder.encode(docs, show_progress_bar=True)
embs = np.array(embs, dtype=np.float32)

client = lancedb.connect('./lancedb')

table = client.create_table(
    name=file_name,
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


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

model = SentenceTransformer(
    "jinaai/jina-embeddings-v2-base-zh", # switch to en/zh for English or Chinese
    trust_remote_code=True
)

# control your input sequence length up to 8192
model.max_seq_length = 1024

embeddings = model.encode([
    'How is the weather today?',
    '今天天气怎么样?'
])
print(cos_sim(embeddings[0], embeddings[1]))

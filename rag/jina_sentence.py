#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

cos_sim = lambda a,b: (a @ b.T) / (norm(a)*norm(b))
model = SentenceTransformer('jinaai/jina-embeddings-v2-base-zh', trust_remote_code=True)
embeddings = model.encode(['How is the weather today?', '今天天气怎么样?'])
print(cos_sim(embeddings[0], embeddings[1]))

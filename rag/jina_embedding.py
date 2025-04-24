#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
from transformers import AutoModel
from numpy.linalg import norm

cos_sim = lambda a,b: (a @ b.T) / (norm(a)*norm(b))
model = AutoModel.from_pretrained('jinaai/jina-embeddings-v2-base-zh', trust_remote_code=True, torch_dtype=torch.bfloat16)
embeddings = model.encode(['How is the weather today?', '今天天气怎么样?'])
print(cos_sim(embeddings[0], embeddings[1]))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch

'''
from transformers import BertTokenizer, BertForMaskedLM
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')
input_text = "I am a passionate boy and [MASK]"
num_predictions = 10

for i in range(num_predictions):
    # 对输入进行编码
    input = tokenizer.encode(input_text, return_tensors="pt")
    mask_index = torch.where(input == tokenizer.mask_token_id)[1]

    # 使用 BERT 进行预测
    output = model(input, return_dict=True)
    logits = output.logits
    mask_word = logits[0, mask_index, :]

    # 选取预测的词汇
    top_word = torch.topk(mask_word, 1, dim=1).indices[0].item()
    predicted_word = tokenizer.decode([top_word])

    # 添加预测的词汇到句子中，并在句子末尾添加一个新的 "[MASK]"
    input_text = input_text.replace("[MASK]", predicted_word, 1) + " [MASK]"
    print(f"预测的句子: {input_text}")
'''

print()

from transformers import GPT2Tokenizer, GPT2LMHeadModel
tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
model = GPT2LMHeadModel.from_pretrained('gpt2')
input_text = "I am"

input = tokenizer.encode(input_text, return_tensors="pt")

# 创建attention_mask
attention_mask = torch.ones_like(input)

# 设置pad_token_id
pad_token_id = tokenizer.eos_token_id

# 调用模型的生成方法
output = model.generate(input,
                        attention_mask=attention_mask,
                        max_length=1000,
                        pad_token_id=pad_token_id,
                        temperature=0.7,
                        top_k=20,
                        repetition_penalty=1.2)

generated_text = tokenizer.decode(output[0])

print(generated_text)

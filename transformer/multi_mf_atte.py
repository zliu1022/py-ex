#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from transformers import BertTokenizer, BertForMaskedLM
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')

#input_text = "I have [MASK] apples and [MASK] oranges and [MASK] bananas."
input_text = "She is a [MASK] girl and she want to [MASK] with me on [MASK] and [MASK] me very much."
num_mask = input_text.count("[MASK]")

print()

# 循环预测每一个掩盖的词
for i in range(num_mask):
    input = tokenizer.encode(input_text, return_tensors="pt")
    mask_index = torch.where(input == tokenizer.mask_token_id)[1]

    output = model(input, return_dict=True)
    logits = output.logits

    mask_word = logits[0, mask_index, :]
    for j in range(mask_word.shape[0]):
        print('predicted_word, No.', j, 'MASK :')
        top_5_words = torch.topk(mask_word, 10, dim=1).indices[j].tolist()
        for token in top_5_words:
            predicted_word = tokenizer.decode([token])
            print(predicted_word, end=' ')
        print()

    top_5_words = torch.topk(mask_word, 10, dim=1).indices[0].tolist()
    all_predicted_text = input_text
    for token in top_5_words:
        predicted_word = tokenizer.decode([token])
        all_predicted_text = all_predicted_text.replace("[MASK]", predicted_word, 1)
        print(f"预测的句子: {all_predicted_text}")
        all_predicted_text = input_text  # restore the input_text for the next prediction

    # 选取概率最高的词填入句子中
    predicted_word = tokenizer.decode([top_5_words[0]])
    input_text = input_text.replace("[MASK]", predicted_word, 1)

    print('-----')


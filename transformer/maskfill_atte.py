#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from transformers import BertTokenizer, BertForMaskedLM
import torch

# Initialize the tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForMaskedLM.from_pretrained('bert-base-uncased')

# Define the input text
text = "[CLS] I have a [MASK] . [SEP]"
inputs = tokenizer(text, return_tensors='pt')
print(inputs)

# Predict the masked token
outputs = model(**inputs)
predictions = outputs.logits
predicted_index = torch.argmax(predictions[0, 4]).item()
predicted_token = tokenizer.convert_ids_to_tokens([predicted_index])[0]

print(predicted_token)


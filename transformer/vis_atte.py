#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
from transformers import BertTokenizer, BertModel
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load pre-trained BERT model and tokenizer
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name, output_attentions=True)  # Add the output_attentions=True parameter

# Input text
#text = "Here is some text to demonstrate the attention mechanism."
text = "The cat sat on the mat and the dog sat on the couch."

# Tokenize input text and convert to tensors
inputs = tokenizer(text, return_tensors='pt')

# Get attention weights from the BERT model
with torch.no_grad():
    outputs = model(**inputs)
    attention = outputs.attentions

# Visualize attention weights
def plot_attention(text, attention, layer, head):
    tokens = tokenizer.tokenize(text)
    tokens = ['[CLS]'] + tokens + ['[SEP]']
    plt.figure(figsize=(10, 10))
    sns.heatmap(attention[layer][0, head].cpu().numpy(), xticklabels=tokens, yticklabels=tokens, cmap="viridis", linewidths=.5)
    plt.xlabel("Keys")
    plt.ylabel("Queries")
    plt.title(f"Layer {layer+1}, Head {head+1}")
    plt.show()

layer = 0  # Choose the layer (0 to 11 for BERT-base)
head =  0  # Choose the head (0 to 11 for BERT-base)
plot_attention(text, attention, layer, head)

'''
def plot_attention_all_layers_heads(text, attention):
    tokens = tokenizer.tokenize(text)
    tokens = ['[CLS]'] + tokens + ['[SEP]']
    num_layers = len(attention)
    num_heads = attention[0].shape[1]

    for layer in range(num_layers):
        for head in range(num_heads):
            plt.figure(figsize=(10, 10))
            sns.heatmap(attention[layer][0, head].cpu().numpy(), xticklabels=tokens, yticklabels=tokens, cmap="viridis", linewidths=.5)
            plt.xlabel("Keys")
            plt.ylabel("Queries")
            plt.title(f"Layer {layer+1}, Head {head+1}")
            plt.show()

plot_attention_all_layers_heads(text, attention)
'''

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.nn.functional as F

import math
import numpy as np

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


class Transformer(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_heads, dropout):
        super(Transformer, self).__init__()
        self.hidden_size = hidden_size
        self.embedding = nn.Linear(input_size, hidden_size)
        self.pos_encoder = PositionalEncoding(hidden_size, dropout)
        encoder_layer = nn.TransformerEncoderLayer(hidden_size, num_heads, dropout)
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, src):
        src = self.embedding(src)
        src = self.pos_encoder(src)
        output = self.encoder(src)
        output = self.fc(output)
        output = torch.mean(output, dim=0)
        return output

# Generate some random data
data = np.random.rand(10, 20, 100)
data = torch.tensor(data).float()

# Create a Transformer instance and process the data
transformer = Transformer(input_size=100, hidden_size=256, num_layers=6, num_heads=8, dropout=0.1)
output = transformer(data)
print(output.shape)


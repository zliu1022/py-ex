#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import math

'''
class Transformer(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_heads, dropout):
        super(Transformer, self).__init__()

        self.embedding = nn.Embedding(input_size, hidden_size)
        self.pos_encoder = PositionalEncoding(hidden_size, dropout)
        self.encoder_layer = nn.TransformerEncoderLayer(hidden_size, num_heads, dropout)
        self.encoder = nn.TransformerEncoder(self.encoder_layer, num_layers)
        self.decoder_layer = nn.TransformerDecoderLayer(hidden_size, num_heads, dropout)
        self.decoder = nn.TransformerDecoder(self.decoder_layer, num_layers)
        self.out = nn.Linear(hidden_size, input_size)

    def forward(self, src, tgt):
        src = self.embedding(src)
        src = self.pos_encoder(src)
        memory = self.encoder(src)
        tgt = self.embedding(tgt)
        tgt = self.pos_encoder(tgt)
        output = self.decoder(tgt, memory)
        output = self.out(output)
        return output

class Transformer(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_heads, dropout):
        super(Transformer, self).__init__()
        self.encoder_layer = nn.TransformerEncoderLayer(hidden_size, num_heads, dropout)
        self.encoder = nn.TransformerEncoder(self.encoder_layer, num_layers)
        self.input_embedding = nn.Linear(input_size, hidden_size)
        self.output_embedding = nn.Linear(hidden_size, input_size)

    def forward(self, x):
        x = self.input_embedding(x)
        x = x.permute(1, 0, 2)
        x = self.encoder(x)
        x = x.permute(1, 0, 2)
        x = self.output_embedding(x)
        return x
'''

class Transformer(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_heads, dropout):
        super(Transformer, self).__init__()
        self.embedding = nn.Linear(input_size, hidden_size)
        self.positional_encoding = PositionalEncoding(hidden_size, dropout)
        self.encoder_layer = nn.TransformerEncoderLayer(hidden_size, num_heads, dropout)
        self.encoder = nn.TransformerEncoder(self.encoder_layer, num_layers)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, src, src_mask=None):
        src = self.embedding(src)
        src = src * math.sqrt(src.shape[-1])
        src = self.positional_encoding(src)
        src = self.encoder(src, src_mask)
        src = torch.mean(src, dim=0)
        src = self.fc(src)
        return src

class TransformerEncoderLayer(nn.Module):
    def __init__(self, hidden_size, num_heads, dropout):
        super(TransformerEncoderLayer, self).__init__()
        self.self_attn = nn.MultiheadAttention(hidden_size, num_heads, dropout)
        self.feed_forward = nn.Sequential(
            nn.Linear(hidden_size, 4 * hidden_size),
            nn.ReLU(),
            nn.Linear(4 * hidden_size, hidden_size),
        )
        self.norm1 = nn.LayerNorm(hidden_size)
        self.norm2 = nn.LayerNorm(hidden_size)
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, src, src_mask=None):
        src2 = self.norm1(src)
        src2, _ = self.self_attn(src2, src2, src2, attn_mask=src_mask)
        src = src + self.dropout1(src2)
        src2 = self.norm2(src)
        src2 = self.feed_forward(src2)
        src = src + self.dropout2(src2)
        return src

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, dropout, max_len=5000):
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

transformer = Transformer(input_size=100, hidden_size=256, num_layers=6, num_heads=8, dropout=0.1)
src = torch.randint(low=0, high=100, size=(10, 32)) # 10 sequences of length 32
tgt = torch.randint(low=0, high=100, size=(8, 32)) # 8 sequences of length 32
output = transformer(src, tgt)

print('src')
print(src)
print()
print('tgt')
print(tgt)
print()
print('output')
print(output)
print()

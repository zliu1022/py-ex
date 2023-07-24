#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import torch
import torch.nn as nn
import torch.nn.functional as F

import math
import numpy as np

import torch
import torch.nn as nn


class Transformer(nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, num_heads, dropout):
        super().__init__()

        # Encoder
        self.encoder_layer = nn.TransformerEncoderLayer(hidden_size, num_heads, dropout)
        self.encoder_norm = nn.LayerNorm(hidden_size)
        self.encoder = nn.TransformerEncoder(self.encoder_layer, num_layers)

        # Decoder
        self.decoder_layer = nn.TransformerDecoderLayer(hidden_size, num_heads, dropout)
        self.decoder_norm = nn.LayerNorm(hidden_size)
        self.decoder = nn.TransformerDecoder(self.decoder_layer, num_layers)

        # Input embedding
        self.input_embedding = nn.Linear(input_size, hidden_size)

        # Output embedding
        self.output_embedding = nn.Linear(hidden_size, input_size)

    def forward(self, input_tensor, target_tensor):
        # Embed input and target sequences
        input_embedded = self.input_embedding(input_tensor)
        target_embedded = self.input_embedding(target_tensor)

        # Encode input sequence
        encoder_output = self.encoder(input_embedded)

        # Decode target sequence conditioned on encoder output
        decoder_output = self.decoder(target_embedded, encoder_output)

        # Embed decoder output to get prediction logits
        output_logits = self.output_embedding(decoder_output)

        return output_logits

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


# Generate some random data
data = np.random.rand(10, 20, 100)
data = torch.tensor(data).float()

# Create a Transformer instance and process the data
transformer = Transformer(input_size=100, hidden_size=256, num_layers=6, num_heads=8, dropout=0.1)
output = transformer(data)
print(output.shape)

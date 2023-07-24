#!/usr/bin/env python3
# -*- coding: utf-8 -*-

q = 34  # Quotation mark character
l = [
    "q = 34  # Quotation mark character",
    "l = [",
    "    ",
    "]",
    "for i in range(0, 2):          # Print opening code",
    "    print(l[i])",
    "for i in range(len(l)):        # Print string array",
    "    print(l[2] + chr(q) + l[i] + chr(q) + ',')",
    "for i in range(3, len(l)):     # Print this code",
    "    print(l[i])",
]

for i in range(0, 2):          # Print opening code
    print(l[i])
for i in range(len(l)):        # Print string array
    print(l[2] + chr(q) + l[i] + chr(q) + ',')
for i in range(3, len(l)):     # Print this code
    print(l[i])


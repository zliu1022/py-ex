#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
from pymongo import MongoClient
import itertools

'''
读取mongodb，x库，q表，里面存放的是围棋死活题
每个document的格式如下，其中 no字段是题目编号，也是唯一索引，
其中的 prepos字段就是死活题里黑子、白子的"初始摆放位置"

读取每个document里的"初始摆放位置"，
功能函数1：对初始位置进行旋转对称，应该有8种
功能函数2：在8种旋转对称位置中，找到最靠近棋盘左上角（横轴19，纵轴1）的初始位置
功能函数3：对于每一题，左上角初始位置，和其他document的左上角初始位置，进行匹配：

如果所有棋子的颜色和位置都相同，表示完全一样
如果有部份相同，则统计出相同的百分比
每个document的格式如下：
{
    "no": "1",
    "prepos": {
        "b": [
            "rb",
            "rc",
            "qd",
            "pd",
            "oc",
            "nc",
            "lc",
            "ra"
        ],
        "w": [
            "sc",
            "rd",
            "re",
            "qf",
            "qc",
            "pc",
            "qb",
            "qa",
            "ob"
        ]
    },
}
'''

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['101']
collection = db['q']

# Mapping letters to numbers, skipping 'i'
#letters = [chr(c) for c in range(ord('a'), ord('t')+1) if c != ord('i')]
letters = [chr(c) for c in range(ord('a'), ord('s')+1)]
letter_to_num = {l: i+1 for i, l in enumerate(letters)}
num_to_letter = {i+1: l for i, l in enumerate(letters)}
N = 19  # Go board size

# Function to convert position label to (x, y) coordinates
def pos_label_to_coord(pos_label):
    letter_x = pos_label[0]
    letter_y = pos_label[1]
    x = letter_to_num[letter_x]
    y = letter_to_num[letter_y]
    return x, y

# Function to convert (x, y) coordinates back to position label
def coord_to_pos_label(x, y):
    letter_x = num_to_letter[x]
    letter_y = num_to_letter[y]
    return letter_x + letter_y

# Symmetry transformations
def identity(x, y):
    return x, y

def rotate90(x, y):
    return N - y +1, x

def rotate180(x, y):
    return N - x +1, N - y +1

def rotate270(x, y):
    return y, N - x +1

def reflect_vertical(x, y):
    return N - x +1, y

def reflect_horizontal(x, y):
    return x, N - y +1

def reflect_diag_main(x, y):
    return y, x

def reflect_diag_anti(x, y):
    return N - y +1, N - x +1

transformations = [identity, rotate90, rotate180, rotate270,
                   reflect_vertical, reflect_horizontal,
                   reflect_diag_main, reflect_diag_anti]

# Function to generate symmetries for a given stone configuration
def generate_symmetries(stones):
    symmetries = []
    for transform in transformations:
        transformed_stones = []
        for x, y, color in stones:
            x_t, y_t = transform(x, y)
            transformed_stones.append((x_t, y_t, color))
        symmetries.append(transformed_stones)
    return symmetries

# Function to create a canonical representation of stones
def canonical_form(stones):
    # Sort stones by (x, y, color)
    stones_sorted = sorted(stones)
    # Create a string representation
    stones_str = ';'.join(f"{x}_{y}_{color}" for x, y, color in stones_sorted)
    return stones_str

# Read all documents and process them
documents = list(collection.find())
#documents = list(collection.find({'no': '4958'}))
canonical_forms = {}  # Map document 'no' to its canonical form
for doc in documents:
    no = doc['no']
    prepos = doc.get('prepos')
    if not prepos:
        print(doc)
        continue
    stones = []
    # Convert positions to coordinates
    for color, positions in prepos.items():
        for pos_label in positions:
            x, y = pos_label_to_coord(pos_label)
            stones.append((x, y, color))
    # Generate symmetries
    symmetries = generate_symmetries(stones)
    # Get canonical form (minimum sorted string of stones)
    canonical_strings = []
    for sym_stones in symmetries:
        # Get sorted stones
        stones_str = canonical_form(sym_stones)
        canonical_strings.append(stones_str)
    # Select the minimal canonical form
    min_canonical_str = min(canonical_strings)
    canonical_forms[no] = min_canonical_str
    #print(canonical_strings)
    #print(min_canonical_str)
    # Update the document with canonical form if needed
    # collection.update_one({'no': no}, {'$set': {'canonical': min_canonical_str}})

# Group documents by their canonical forms
canonical_groups = {}
for no, canon_str in canonical_forms.items():
    if canon_str in canonical_groups:
        canonical_groups[canon_str].append(no)
    else:
        canonical_groups[canon_str] = [no]

# Identify identical documents
identical_groups = [group for group in canonical_groups.values() if len(group) > 1]

# Output identical groups
print("Identical problems:")
for group in identical_groups:
    print("Problems with identical positions:", group)

quit()
# Compute percentage of matching stones between documents
def matching_percentage(stones1, stones2):
    set1 = set((x, y, color) for x, y, color in stones1)
    set2 = set((x, y, color) for x, y, color in stones2)
    matching = set1 & set2
    total = set1 | set2
    percentage = (len(matching) / len(total)) * 100 if total else 100
    return percentage

# Compare each document's canonical position with others
for i, doc1 in enumerate(documents):
    no1 = doc1['no']
    prepos1 = doc1['prepos']
    stones1 = []
    for color, positions in prepos1.items():
        for pos_label in positions:
            x, y = pos_label_to_coord(pos_label)
            stones1.append((x, y, color))
    # Get the canonical stones for document 1
    symmetries1 = generate_symmetries(stones1)
    min_stones1 = min(symmetries1, key=lambda s: canonical_form(s))
    for j in range(i+1, len(documents)):
        doc2 = documents[j]
        no2 = doc2['no']
        prepos2 = doc2['prepos']
        stones2 = []
        for color, positions in prepos2.items():
            for pos_label in positions:
                x, y = pos_label_to_coord(pos_label)
                stones2.append((x, y, color))
        # Get the canonical stones for document 2
        symmetries2 = generate_symmetries(stones2)
        min_stones2 = min(symmetries2, key=lambda s: canonical_form(s))
        # Compute matching percentage
        percentage = matching_percentage(min_stones1, min_stones2)
        if percentage > 0:
            print(f"Matching between problem {no1} and {no2}: {percentage:.2f}%")

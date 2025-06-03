#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
from matchq import canonicalize_positions
import json
from pymongo import MongoClient
from pprint import pprint
from config import db_name

def parse_svg(svg_content):
    # Parse the SVG content
    root = ET.fromstring(svg_content)
    
    # Namespace handling
    ns = {'svg': 'http://www.w3.org/2000/svg'}
    ET.register_namespace('', ns['svg'])
    
    # Extract grid lines positions
    x_positions = set()
    y_positions = set()
    for element in root.findall('.//{*}line'):
        x1 = float(element.get('x1'))
        x2 = float(element.get('x2'))
        y1 = float(element.get('y1'))
        y2 = float(element.get('y2'))
        if x1 == x2:  # Vertical line
            x_positions.add(x1)
        if y1 == y2:  # Horizontal line
            y_positions.add(y1)
    
    x_positions = sorted(x_positions)
    y_positions = sorted(y_positions)
    
    # Map x_positions to columns ('k' to 's')
    letters = list('abcdefghijklmnopqrs')  # 19 letters
    col_letters = letters[10:19]  # 'k' to 's'
    x_to_col = dict(zip(x_positions, col_letters))
    
    # Map y_positions to rows ('a' to 'i')
    row_letters = letters[0:9]  # 'a' to 'i'
    y_to_row = dict(zip(y_positions, row_letters))
    
    # Extract stones
    stones = {'b': [], 'w': []}
    for element in root.findall('.//{*}circle'):
        fill = element.get('fill')
        if fill not in ('black', 'white'):
            continue  # Skip other circles (e.g., center point)
        cx = float(element.get('cx'))
        cy = float(element.get('cy'))
        
        # Find the closest x and y positions
        closest_x = min(x_positions, key=lambda x: abs(x - cx))
        closest_y = min(y_positions, key=lambda y: abs(y - cy))
        
        col = x_to_col[closest_x]
        row = y_to_row[closest_y]
        
        coordinate = col + row
        if fill == 'black':
            stones['b'].append(coordinate)
        elif fill == 'white':
            stones['w'].append(coordinate)
    
    # Sort the lists if necessary
    stones['b'] = sorted(stones['b'])
    stones['w'] = sorted(stones['w'])
    
    return stones

def search(pos):
    stones_key = canonicalize_positions(pos)
    stones_key_list = [list(item) for item in stones_key]
    min_pp = json.dumps(stones_key_list, sort_keys=True)

    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]

    col = db['q']
    docs = col.find({'min_pp': min_pp})
    for doc in docs:
        uid = doc.get('_id')
        level = doc.get('level')
        qtype = doc.get('qtype')
        publicid = doc.get('publicid')
        print(f'q {publicid} {level} {qtype} {uid}')

    for n in range(1,6):
        col = db[f'book_{n}_q']
        docs = col.find({'min_pp': min_pp})

        for doc in docs:
            uid = doc.get('_id')
            publicid = doc.get('publicid')
            book_id = doc.get('book_id')
            url_frombook = doc.get('url_frombook')

            col_book = db[f'book_{n}']
            ret = col_book.find_one({'id': book_id})
            print(f'book_{n}_q {publicid} {book_id} {url_frombook} {uid} {ret.get('name')}')

def svg_to_pos(svg_name):
    with open(svg_name, "r", encoding="utf-8") as file:
        svg_content = file.read()
    pos = parse_svg(svg_content)

    print(svg_name)
    pprint(pos)
    return pos

if __name__ == "__main__":
    svg_name = 'book/302086.svg'
    pos = svg_to_pos(svg_name)
    search(pos)

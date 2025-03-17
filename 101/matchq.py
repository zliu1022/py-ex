#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymongo
import itertools
from collections import defaultdict

# Function to convert position string to coordinates
def pos_to_coord(pos):
    # Mapping from letters to numbers for columns and rows
    # Letters 'a' to 's' correspond to numbers 1 to 19
    letter_to_num = {chr(ord('a') + i): i + 1 for i in range(19)}

    x_letter, y_letter = pos[0], pos[1]
    x = 20 - letter_to_num[x_letter]  # x decreases from left to right
    y = letter_to_num[y_letter]       # y increases from top to bottom
    return (x, y)

# Function to convert coordinates back to position string
def coord_to_pos(coord):
    x_num, y_num = coord
    x_letter = chr( ord('a') + (19 - x_num) )
    y_letter = chr( ord('a') + (y_num -1) )
    return x_letter + y_letter

# Define symmetry transformations
def symmetries(x, y):
    n = 19
    syms = []
    syms.append( ( x,  y) )                   # Identity
    syms.append( ( n+1 - y,  x) )             # Rotate 90
    syms.append( ( n+1 - x, n+1 - y) )        # Rotate 180
    syms.append( (      y, n+1 - x) )         # Rotate 270
    syms.append( ( n+1 - x,       y) )        # Reflect over vertical axis
    syms.append( (      x, n+1 - y) )         # Reflect over horizontal axis
    syms.append( (      y,       x) )         # Reflect over main diagonal
    syms.append( ( n+1 - y, n+1 - x) )        # Reflect over anti-diagonal
    return syms

# Function to canonicalize positions
def canonicalize_positions(prepos):
    positions = []
    # Convert positions to coordinates
    for color_key in ['b', 'w']:
        color = 'B' if color_key == 'b' else 'W'
        for pos_str in prepos.get(color_key, []):
            x, y = pos_to_coord(pos_str)
            positions.append( (color, x, y) )

    # positions: list of tuples (color, x, y)
    # Apply all symmetries and pick the one with the minimal representation
    min_representation = None
    for i in range(8):
        transformed_positions = []
        for color, x, y in positions:
            # Apply the i-th symmetry
            sym = symmetries(x, y)[i]
            transformed_positions.append( (color, sym[0], sym[1]) )
        # Sort positions
        transformed_positions.sort()
        # Represent as a string
        representation = ''.join(f'{color}{x:02d}{y:02d}' for color, x, y in transformed_positions)
        # Keep the minimal representation
        if min_representation is None or representation < min_representation:
            min_representation = representation
            min_positions = transformed_positions
    return min_representation, min_positions

if __name__ == "__main__":
    # Connect to MongoDB
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['101']
    collection = db['q']

    # Read documents and process positions
    canonical_positions = defaultdict(list)  # mapping from representation to list of document IDs
    doc_positions = {}  # mapping from document ID to canonical positions
    #docs = list(collection.find({'no': '4958'}))
    docs = list(collection.find())

    for doc in docs:
        doc_id = str(doc['no'])
        prepos = doc.get('prepos')
        if not prepos:
            print(doc)
            continue
        # Canonicalize positions
        representation, canon_positions = canonicalize_positions(prepos)
        #print(representation)
        #print(canon_positions)

        canonical_positions[representation].append(doc_id)
        doc_positions[doc_id] = set( (color, x, y) for color, x, y in canon_positions )

        #print(canonical_positions)
        #print(doc_positions)

    # Find identical and similar documents
    identical_docs = {}  # mapping from document ID to list of identical document IDs
    similar_docs = {}    # mapping from document ID to list of tuples (doc ID, similarity percentage)

    for representation, doc_ids in canonical_positions.items():
        if len(doc_ids) > 1:
            # Documents with identical positions
            for doc_id in doc_ids:
                identical_docs[doc_id] = [d for d in doc_ids if d != doc_id]
    print(identical_docs)

    # Compute similarities between all pairs (could be optimized)
    all_doc_ids = list(doc_positions.keys())
    for i, doc_id1 in enumerate(all_doc_ids):
        positions1 = doc_positions[doc_id1]
        for doc_id2 in all_doc_ids[i+1:]:
            positions2 = doc_positions[doc_id2]
            # Compute Jaccard similarity
            intersection = positions1 & positions2
            union = positions1 | positions2
            similarity = len(intersection) / len(union) * 100
            if similarity > 0 and similarity < 100:
                similar_docs.setdefault(doc_id1, []).append( (doc_id2, similarity) )
                similar_docs.setdefault(doc_id2, []).append( (doc_id1, similarity) )

    # Output results
    # Identical documents
    print("Identical Documents:")
    for doc_id, duplicates in identical_docs.items():
        print(f"Document {doc_id} is identical to documents: {', '.join(duplicates)}")

    quit()

    # Similar documents
    print("\nSimilar Documents:")
    for doc_id, similarities in similar_docs.items():
        for other_doc_id, similarity in similarities:
            print(f"Document {doc_id} is {similarity:.2f}% similar to document {other_doc_id}")

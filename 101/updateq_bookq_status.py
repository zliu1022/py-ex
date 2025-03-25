#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import db_name

# 已经抓取一部分book_q到q表,带上了 url_frombook和status
# 把 url_frombook和status更新到 book_5_q，后续根据book_5_q来记录是否更新过

# Replace the URI string with your MongoDB deployment's connection string.
client = MongoClient('mongodb://localhost:27017/')

db = client[db_name]

# Access the 'q' and 'book_5_q' collections
q_collection = db['q']
book_5_q_collection = db['book_5_q']

# Find all documents in 'q' that have the 'url_frombook' field
q_documents = q_collection.find({'url_frombook': {'$exists': True}})

# Iterate over each document
for q_doc in q_documents:
    url_frombook = q_doc['url_frombook']
    publicid = q_doc.get('publicid')
    status = q_doc.get('status')
    min_pp = q_doc.get('min_pp')

    # Update the matching document in 'book_5_q'
    update_result = book_5_q_collection.update_one(
        {'url_frombook': url_frombook},
        {'$set': {'publicid': publicid, 'status': status, 'min_pp': min_pp}}
    )

    # Print the update status
    print(f"Updating document with url_frombook: {url_frombook}", end='')
    if update_result.matched_count > 0:
        print(f" - Matched: {update_result.matched_count} Modified: {update_result.modified_count}")
    else:
        print(" - No matching document found in 'book_5_q' collection.")

# Close the connection
client.close()

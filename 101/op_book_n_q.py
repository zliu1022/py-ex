#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import db_name, base_url

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Modify the URI as needed

# Select the database and collection
db = client[db_name]
collection = db['book_4_q']

# Define the search pattern and the replacement string
search_pattern = '/book/49591/0/'
replacement_string = '/book/49591/144846/'

# Find all documents where 'url_frombook' starts with '/book/49591/0/'
query = {"url_frombook": {"$regex": "^/book/49591/0/"}}

# Iterate over the matching documents
for doc in collection.find(query):
    original_url = doc['url_frombook']
    # Replace the specified part of the string
    updated_url = original_url.replace(search_pattern, replacement_string)
    # Update the document in the collection
    collection.update_one(
        {'_id': doc['_id']},
        {
            '$set': {'url_frombook': updated_url},
            '$unset': {'status': ''}
        }
    )
    print(f"Updated document ID {doc['_id']}: '{original_url}' -> '{updated_url}'")

print("All matching documents have been updated.")


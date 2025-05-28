#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import db_name, base_url

# Step 1: Connect to MongoDB
# Replace the connection string with your MongoDB URI if it's different
client = MongoClient('mongodb://localhost:27017/')

# Step 2: Access the 'db' database
db = client[db_name]  # Replace 'db' with your actual database name if different

# Step 3: Access the required collections
book_ex = db['book_ex']
book_1_q = db['book_1_q']
book_ex_q = db['book_ex_q']

# Step 4: Find documents in 'book_ex' where username is 'kenny' and get their '_id' values
kenny_docs_cursor = book_ex.find({'username': 'kenny'}, {'id': 1})

# Collect '_id's into a list
kenny_ids = [doc['id'] for doc in kenny_docs_cursor]

# Debug: Print the list of '_id's (Optional)
print(f"IDs of documents where username is 'kenny': {kenny_ids}")

# Step 5: Find documents in 'book_1_q' where 'book_id' is in the list of 'kenny_ids'
# Note: Ensure that 'book_id' field in 'book_1_q' is of the same type as '_id' in 'book_ex' (i.e., ObjectId)
query = {'book_id': {'$in': kenny_ids}}
matching_docs_cursor = book_1_q.find(query)

# Collect matching documents into a list
matching_docs = list(matching_docs_cursor)

# Debug: Print the number of documents found (Optional)
print(f"Number of documents to move: {len(matching_docs)}")

# Step 6: Insert matching documents into 'book_ex_q' collection and remove them from 'book_1_q'
if matching_docs:
    # Insert documents into 'book_ex_q'
    insert_result = book_ex_q.insert_many(matching_docs)
    print(f"Inserted {len(insert_result.inserted_ids)} documents into 'book_ex_q'.")
    
    # Remove documents from 'book_1_q'
    delete_result = book_1_q.delete_many(query)
    print(f"Deleted {delete_result.deleted_count} documents from 'book_1_q'.")
else:
    print("No matching documents found to move.")

# Step 7: Close the MongoDB connection (Optional in scripts; necessary in some applications)
client.close()

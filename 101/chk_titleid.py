#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
from pymongo import MongoClient

# Configure your MongoDB connection here
MONGO_URI = 'mongodb://localhost:27017/'
DATABASE_NAME = '101'
COLLECTION_NAME = 'q'

def extract_number_from_filename(filename):
    match = re.match(r'(\d+)\.html$', filename)
    if match:
        return int(match.group(1))
    return None

def extract_number_from_title(content):
    # Use regex to extract content between <title> and </title>
    title_match = re.search(r'<title>\s*(.*?)\s*</title>', content, re.DOTALL)
    if title_match:
        title = title_match.group(1)
        # Extract the number after 'Q-' and before ' - '
        num_match = re.search(r'Q-(\d+)', title)
        if num_match:
            return int(num_match.group(1))
    return None

def main():
    # Directory containing the HTML files
    directory = './.cache'  # Current directory, change it if necessary

    # Initialize MongoDB client
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            num_fname = extract_number_from_filename(filename)
            if num_fname is None:
                continue  # Skip files that don't match the pattern

            # Read the content of the file
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            num_title = extract_number_from_title(content)
            if num_title is None:
                print(f"Cannot find number in title of file: {filename}")
                continue

            if num_fname != num_title:
                print(f"Filename number and title number do not match in file {filename}: title number {num_title}")
                pass
            else:
                continue
                # Update MongoDB document
                result = collection.update_one(
                    {'url_no': num_fname},
                    {'$set': {'title_id': num_title}}
                )
                if result.matched_count == 0:
                    print(f"No document found with url_no = {num_fname} in MongoDB.")
                else:
                    print(f"Updated document with url_no = {num_fname} in MongoDB.")

    # Close the MongoDB client
    client.close()

if __name__ == '__main__':
    main()

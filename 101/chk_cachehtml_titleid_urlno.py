#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 检查cache目录中html文件的title和url_no是否一致

import os
import re
from pymongo import MongoClient
from config import db_name

# Configure your MongoDB connection here
MONGO_URI = 'mongodb://localhost:27017/'
COLLECTION_NAME = 'q'

def extract_number_from_filename(filename):
    match = re.match(r'(\d+)\.html$', filename)
    if match:
        return int(match.group(1))
    return None

def extract_number_and_level_from_title(content):
    # Use regex to extract content between <title> and </title>
    title_match = re.search(r'<title>\s*(.*?)\s*</title>', content, re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        # Extract the number after 'Q-' and the level following it
        num_level_match = re.search(r'Q-(\d+)\s*-\s*([^-]+?)\s*-\s*', title)
        if num_level_match:
            num_title = int(num_level_match.group(1))
            level_title = num_level_match.group(2).strip()
            return num_title, level_title
    return None, None

def main():
    # Directory containing the HTML files
    directory = './.cache'  # Current directory, change it if necessary

    # Initialize MongoDB client
    client = MongoClient(MONGO_URI)
    db = client[db_name]
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

            num_title, level_title = extract_number_and_level_from_title(content)
            if num_title is None:
                print(f"Cannot find number in title of file: {filename}")
                continue

            if num_fname != num_title and level_title != '题库':
                #print(f"Filename number and title number do not match in file {filename}: title number ./getq.py {level_title} {num_title}")
                print(f"./getq.py {level_title} {num_title}")
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

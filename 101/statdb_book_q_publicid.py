#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from config import db_name
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client[db_name]

# Get publicid set from q collection, handling missing and non-integer values
publicid_set = set()
for doc in db.q.find({}, {'publicid': 1}):
    publicid = doc.get('publicid')
    if publicid is not None and publicid != '':
        try:
            publicid_int = int(publicid)
            publicid_set.add(publicid_int)
        except ValueError:
            # Handle non-integer publicid values here
            print(f"Non-integer publicid found: '{publicid}'")
            continue
    else:
        # Handle None or empty string publicid values
        #print(f"Missing or empty publicid found")
        continue

def analyze_collection(collection_name):
    # Get unique url_no values
    url_no_values = db[collection_name].find({'status': { '$ne': 2 }}, {'url_no': 1})
    url_no_int_set = set()
    for doc in url_no_values:
        url_no = doc.get('url_no')
        if url_no is not None and url_no != '':
            try:
                url_no_int = int(url_no)
                url_no_int_set.add(url_no_int)
            except ValueError:
                # Handle non-integer url_no values here
                print(f"Non-integer url_no found: '{url_no}' in collection {collection_name}")
                continue
        else:
            # Handle None or empty string url_no values
            #print(f"Missing or empty url_no found in collection {collection_name}")
            continue

    # url_no not in publicid_set
    url_no_not_in_q = url_no_int_set - publicid_set

    # Results
    total_unique_url_no = len(url_no_int_set)
    url_no_not_in_q_count = len(url_no_not_in_q)

    return total_unique_url_no, url_no_not_in_q_count

# Function 1: Per collection analysis
for n in range(1, 6):
    collection_name = f'book_{n}_q'
    total_unique_url_no, url_no_not_in_q_count = analyze_collection(collection_name)
    print(f'Collection: {collection_name}')
    print(f'Total unique url_no: {total_unique_url_no}')
    print(f'url_no not in q: {url_no_not_in_q_count}\n')

# Function 2: Combined collections analysis
def analyze_all_collections():
    url_no_int_set = set()
    for n in range(1, 6):
        collection_name = f'book_{n}_q'
        url_no_values = db[collection_name].find({ 'status': { '$ne': 2 }  }, {'url_no': 1})
        for doc in url_no_values:
            url_no = doc.get('url_no')
            if url_no is not None and url_no != '':
                try:
                    url_no_int = int(url_no)
                    url_no_int_set.add(url_no_int)
                except ValueError:
                    print(f"Non-integer url_no found: '{url_no}' in collection {collection_name}")
                    continue
            else:
                #print(f"Missing or empty url_no found in collection {collection_name}")
                continue

    url_no_not_in_q = url_no_int_set - publicid_set
    total_unique_url_no = len(url_no_int_set)
    url_no_not_in_q_count = len(url_no_not_in_q)

    return total_unique_url_no, url_no_not_in_q_count

total_unique_url_no, url_no_not_in_q_count = analyze_all_collections()
print('Combined Collections')
print(f'Total unique url_no: {total_unique_url_no}')
print(f'url_no not in q: {url_no_not_in_q_count}')

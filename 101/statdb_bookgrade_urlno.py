#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pymongo import MongoClient
from config import db_name

# 统计每个 book_n_q中唯一的 url_no个数
# 统计所有 book_n_q中唯一的 url_no个数,返回
def stat_unique_urlno():
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]

    #book_collections = ['book_1_q', 'book_2_q', 'book_3_q', 'book_4_q', 'book_5_q']
    book_collections = ['book_5_q']

    unique_url_nos = set()

    for col_name in book_collections:
        collection = db[col_name]

        # Obtain distinct 'url_no's in the current collection
        url_nos = collection.distinct('url_no')
        print(f"{col_name} {len(url_nos)} unique 'url_no'")

        unique_url_nos.update(url_nos)

    print(f"all book {len(unique_url_nos)} unique 'url_no'")
    print()

    client.close()
    return list(unique_url_nos)

# 比对所有book_n_q中的唯一url_no和grade中的唯一url_no
def stat_book_grade_unique(unique_url_nos):
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]
    grade_collection = db['grade']

    grade_url_nos = set(grade_collection.distinct('url_no'))
    print(f"grade unique 'url_no' {len(grade_url_nos)}")

    # Find 'url_no's that are in both sets
    url_nos_in_grade = unique_url_nos.intersection(grade_url_nos)
    # Find 'url_no's that are only in the book collections
    url_nos_not_in_grade = unique_url_nos.difference(grade_url_nos)

    print(f"'url_no' in book_n_q and grade: {len(url_nos_in_grade)}")
    print(f"'url_no' in book_n_q NOT in 'grade': {len(url_nos_not_in_grade)}")

    client.close()
    return {
        'count_in_grade': len(url_nos_in_grade),
        'count_not_in_grade': len(url_nos_not_in_grade),
        'url_nos_in_grade': list(url_nos_in_grade),
        'url_nos_not_in_grade': list(url_nos_not_in_grade)
    }

def stat_book_level(unique_url_nos):
    """
    For the unique 'url_no's, count the number of documents for each 'url_level'.
    The 'url_level's are sorted according to the specified order:
    15K, 14K, ..., 1K, 1D, 2D, ..., 7D
    """
    # Connect to MongoDB
    client = MongoClient("mongodb://localhost:27017/")
    db = client[db_name]

    # List of book collection names
    #book_collections = ['book_1_q', 'book_2_q', 'book_3_q', 'book_4_q', 'book_5_q']
    book_collections = ['book_5_q']

    # Define the custom sort order for 'url_level's
    url_level_order = ['15K', '14K', '13K', '12K', '11K', '10K', '9K', '8K', '7K', '6K', '5K', '4K',
                       '3K', '2K', '1K', '1D', '2D', '3D', '4D', '5D', '6D', '7D']

    # Prepare a dictionary to hold counts for each 'url_level'
    url_level_counts = {}

    # Set to keep track of processed 'url_no's to avoid duplicates
    processed_url_nos = set()

    # Convert the set to a list for batching
    unique_url_no_list = list(unique_url_nos)

    # Define batch size
    batch_size = 1000

    # Process 'url_no's in batches to handle large sets efficiently
    for i in range(0, len(unique_url_no_list), batch_size):
        batch_url_nos = unique_url_no_list[i:i+batch_size]

        # For each collection, find documents with 'url_no's in the current batch
        for col_name in book_collections:
            collection = db[col_name]
            # Query to find documents with 'url_no's in the batch and not already processed
            documents = collection.find(
                {'url_no': {'$in': batch_url_nos}},
                {'url_no': 1, 'url_level': 1}
            )

            # Iterate over the documents
            for doc in documents:
                url_no = doc['url_no']
                url_level = doc.get('url_level', 'Unknown')  # Default to 'Unknown' if 'url_level' missing

                if url_no not in processed_url_nos:
                    # Increment the count for this 'url_level'
                    url_level_counts[url_level] = url_level_counts.get(url_level, 0) + 1
                    # Mark 'url_no' as processed
                    processed_url_nos.add(url_no)

        #print(f"Processed batch {i//batch_size + 1} of {len(unique_url_no_list)//batch_size + 1}")

    # Close the MongoDB connection
    client.close()

    # Sort the 'url_level's according to the specified order
    sorted_url_levels = []
    for level in url_level_order:
        count = url_level_counts.get(level, 0)
        sorted_url_levels.append((level, count))

    # Add any 'url_level's not in the specified order at the end
    other_levels = set(url_level_counts.keys()) - set(url_level_order)
    for level in other_levels:
        count = url_level_counts[level]
        sorted_url_levels.append((level, count))

    # Print the counts for each 'url_level'
    print("\nCounts of 'url_level's:")
    for level, count in sorted_url_levels:
        print(f"{level}: {count}")

    # Return the counts in the specified order
    return sorted_url_levels

if __name__ == "__main__":
    # Function 1: Get unique 'url_no's from book collections
    unique_url_nos = set(stat_unique_urlno())

    # Function 2: Compare with 'grade' collection
    result = stat_book_grade_unique(unique_url_nos)

    # If you want to use the results further, you can access the result dictionary
    # For example, to get the list of 'url_no's not in 'grade' collection:
    urls_not_in_grade = result['url_nos_not_in_grade']

    url_level_counts = stat_book_level(unique_url_nos)


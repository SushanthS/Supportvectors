from text_extractor import *
from postgres_db_setup import *
import os
import psycopg
import faiss
import sys
import numpy as np
import ray
import time

#Note: TODO Flush GPU

dir_path = './books'
# list to store files
file_list = []

#@ray.remote
def convert_doc_to_text():
    conn, cursor = connectDB() 
    print("Convert to text")

    for file in file_list:
        text_list = []
        extract = TextExtraction.to_text(file)
        text_list.append(extract)
        query = """INSERT INTO files(name, type, data) VALUES(%s, %s, %s) RETURNING fileid;"""
        cursor.execute(query, (file, 'txt', extract))

    conn.commit()
    conn.close()
    return

if __name__ == '__main__':

    # Iterate directory
    for path in os.listdir(dir_path):
        # check if current path is a file
        if os.path.isfile(os.path.join(dir_path, path)):
            file_list.append(dir_path + '/' + path)

    print(file_list)

    convert_doc_to_text()

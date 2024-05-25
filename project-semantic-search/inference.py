import os
import sys
import shutil
import psycopg2
from psycopg2.extras import RealDictCursor
import logging as log
import logging.config
import argparse
import time
from datetime import datetime, timezone
from logging.handlers import SysLogHandler
from logging import FileHandler
import hashlib
import json
import pickle
import ray
from ray import serve
from elasticsearch import Elasticsearch
from faiss_index_ray import FaissIndexer
import re

import requests

from svlearn.text import TextExtraction, ChunkText, SentenceEncoder
from svlearn.config import ConfigurationMixin

VERSION="0.1"
log.basicConfig(format='%(asctime)s - %(filename)s:%(lineno)d %(levelname)s - %(message)s',level=logging.INFO)
logger = log.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))
url = "http://localhost:8000/chunker"

class Inference:
    def __init__(self, config) -> None:
        log.info("Processing documents...")
        self.sentence_encoder = SentenceEncoder(config)
        search_schema = config['database']['search-schema']
        # chunk_schema = config['database']['chunk-schema']
        user = config['database']['username']
        password = config['database']['password']
        host = config['database']['server']
        port = config['database']['port']
        self.source_dir = config['documents']['source-dir']
        self.destination_dir = config['documents']['destination-dir']

        # Connection for search schema
        self.search_conn = psycopg2.connect(database=search_schema, user=user, password=password, host=host, port=port)
        self.search_conn.autocommit = True
        self.search_cursor = self.search_conn.cursor(cursor_factory=RealDictCursor)

        # Separate connection for chunk schema.
        self.chunk_conn = psycopg2.connect(dbname=search_schema, user=user, password=password, host=host, port=port)
        self.chunk_conn.autocommit = False
        self.chunk_cursor = self.chunk_conn.cursor(cursor_factory=RealDictCursor)

if __name__ == '__main__':
    config_file = "bootcamp-config-ssv.yaml"

    parser = argparse.ArgumentParser(description='Inference Process')
    parser.add_argument('-c','--config', help='Config file', required=False)
    parser.add_argument('-V','--version', action='version', version='%(prog)s '+VERSION)
    args = parser.parse_args()

    if args.config is not None:
        config_file = args.config

    mixin = ConfigurationMixin()
    config = mixin.load_config(config_file)

    inf = Inference(config)

    while True:
        user_query = input("Enter query:")
        print("user_query is: " + user_query)

        query_embedding = inf.sentence_encoder.encode([user_query])

        fs = FaissIndexer(config)
        index = fs.load_index()
        D, I = index.search(query_embedding, 5)
        index_str_list = re.findall(r'\d+', str(I))
        print(index_str_list)

         
        query = """SELECT chunk_text from "semantic-chunks"."1" WHERE id = %s"""
        for idx, i_str in enumerate(index_str_list):
            i = int(i_str)
            inf.chunk_cursor.execute(query, (i,))
            publisher_records = inf.chunk_cursor.fetchall()
            print("output: ", i, publisher_records)

        '''
        query = """SELECT data from chunks WHERE chunkid = %s"""
        context = ""
        for idx, i_str in enumerate(index_str_list):
            i = int(i_str)
            cursor.execute(query, (i,))
            publisher_records = cursor.fetchall()
            print("output: ", i, publisher_records)
            print(type(publisher_records[0][0]))
            context = context + publisher_records[0][0] + "\n"
            input_list.append(publisher_records[0][0])
        conn.close()
        '''

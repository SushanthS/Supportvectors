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


import requests

from svlearn.text import TextExtraction, ChunkText, SentenceEncoder
from svlearn.config import ConfigurationMixin

VERSION="0.1"
log.basicConfig(format='%(asctime)s - %(filename)s:%(lineno)d %(levelname)s - %(message)s',level=logging.INFO)
logger = log.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))
url = "http://localhost:8000/chunker"

class ChunkerClient:
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
        
    def __del__(self):
        #Closing the connection
        self.search_conn.close()
        self.chunk_conn.close()
        log.info("Done Processing documents...")

    def createChunkTable(self, table_name):
        self.chunk_cursor.execute(""" \
                DROP TABLE IF EXISTS "semantic-chunks"."%s"; \
            """, (table_name,))

        self.chunk_cursor.execute("""CREATE TABLE "semantic-chunks"."%s"( \
                id SERIAL NOT NULL, \
                chunk_text text, \
                chunk_encoded bytea, \
                PRIMARY KEY(id) \
            );""", (table_name,))

    def insertChunks(self, table_name, chunks, vectors):
        log.info("Inserting chunks into table %s, #of chunks: %s", table_name, len(chunks))
        for chunk, vector in zip(chunks, vectors):
            self.chunk_cursor.execute(""" \
                    INSERT into "semantic-chunks"."%s" (chunk_text, chunk_encoded) values(%s, %s)  \
                """, (table_name, chunk, pickle.dumps(vector)))
        self.chunk_conn.commit()

    def encodeChunks(self, chunks):
        vectors={}
        start_time = datetime.now()
        encoded_list = self.sentence_encoder.encode(chunks)
        end_time = datetime.now()
        encode_time = end_time - start_time
        total_encode_time = (encode_time.total_seconds()*1000)+(encode_time.microseconds/1000)
        print(encoded_list.shape)
        vectors["encoded_list"] = encoded_list
        vectors["encode_time"] = total_encode_time
        return vectors



    # https://docs.ray.io/en/latest/ray-core/patterns/limit-running-tasks.html
    @ray.remote
    def postForChunking(req):
        start_time = datetime.now()
        res = requests.post(url, json = req)
        end_time = datetime.now()
        text_chunk_time = end_time - start_time
        chunks = json.loads(res.text)
        return chunks
        

    """ 
        Select files which are not chunked.
        Send each file text to the webservice to get it chunked.
        Receive the chunks and insert the chunks to the chunk schema tables.
        Update the chunked status in the search-schema for the document.

        Chunking is parallelized. 
        TODO: Inserting is not parallelized.  That might need more thought 
        as to multiple db connections, reuse of db connections etc.
    
    """
    def processFiles(self):
        log.info("Starting to process chunks...")
        self.search_cursor.execute("""SELECT * FROM "semantic-search".corpus WHERE chunked IS False OR chunked IS NULL FOR UPDATE """)
        result = self.search_cursor.fetchall()
        if not result:
            log.info("Nothing to process...")
            return
        result_refs = []
        for rec in result:
            file_name = rec["filename"]
            tid =  rec["id"]
            log.info("Posting to the webservice for chunking for file %s", file_name)
            req = {"id": tid, "text" : rec["extracted_text"]}
            memory = 2 * 1024 * 1024 * 1024         # 2GB memory
            result_refs.append(
                # self.postForChunking.options(memory=memory).remote(req)
                self.postForChunking.remote(req)
                )

        # https://docs.ray.io/en/latest/ray-core/tips-for-first-time.html#tip-4-pipeline-data-processing
        while len(result_refs):
            done_id, result_refs = ray.wait(result_refs)
            file_chunk = ray.get(done_id[0])

            table_name = tid = file_chunk["id"]
            chunks = file_chunk["chunks"]
            chunk_time = file_chunk["chunk_time"]

            vectors = self.encodeChunks(chunks)
            encode_time = vectors["encode_time"]
            encoded_list = vectors["encoded_list"]

            log.info(f"Creating table {table_name}")
            self.createChunkTable(table_name)

            log.info(f"Inserting {len(chunks)} chunks into table {table_name}")
            self.insertChunks(table_name, chunks, encoded_list)

            log.info("UPDATE corpus SET chunked=true, vectorized=true, chunk_time_ms=%s where id=%s  ", chunk_time, tid,)
            self.search_cursor.execute("""UPDATE "semantic-search".corpus SET chunked=true, vectorized=true, \
                                       chunk_time_ms=%s, encode_time_ms=%s where id=%s  """, (chunk_time, encode_time, tid,))

        return

if __name__ == '__main__':
    config_file = "bootcamp-config-ssv.yaml"

    parser = argparse.ArgumentParser(description='Text Extractor Process')
    parser.add_argument('-c','--config', help='Config file', required=False)
    parser.add_argument('-V','--version', action='version', version='%(prog)s '+VERSION)
    args = parser.parse_args()

    if args.config is not None:
        config_file = args.config

    ray.init()

    mixin = ConfigurationMixin()
    config = mixin.load_config(config_file)

    pd = ChunkerClient(config)
    pd.processFiles()

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
        search_schema = config['database']['search-schema']
        user = config['database']['username']
        password = config['database']['password']
        host = config['database']['server']
        port = config['database']['port']
        self.source_dir = config['documents']['source-dir']
        self.destination_dir = config['documents']['destination-dir']

        self.search_conn = psycopg2.connect( database=search_schema, user=user, password=password, host=host, port=port)
        self.search_conn.autocommit = True
        self.search_cursor = self.search_conn.cursor(cursor_factory=RealDictCursor)
        
    def __del__(self):
        #Closing the connection
        self.search_conn.close()
        log.info("Done Processing documents...")

    def doFileCleanup(self, file):
        # Once the processing is done, move file to destination folder
        try:
            if os.path.exists(file):
                # os.remove(file)
                shutil.move(file, self.destination_dir)
        except Exception as e:
            errStr = str(e) 
            log.error(errStr)
    
    def getSha512(self, file):
        with open(file, "rb") as f:
            digest = hashlib.file_digest(f, "sha512")
        return digest.hexdigest()

    @ray.remote(num_cpus=1, num_gpus=1)
    def doTextExtract(hash: str, file: str):
        log.info("Processing file %s ", file)
        start_time = datetime.now()
        extracted_text = TextExtraction(file).text_
        end_time = datetime.now()
        text_extraction_time = end_time - start_time
        text_data = {}
        text_data["hash"] = hash
        text_data["file"] = file
        text_data["time"] = text_extraction_time
        text_data["extracted_text"] = extracted_text
        
        return text_data
                
    def processFiles(self):
        self.search_cursor.execute("""select * from "semantic-search".corpus where chunked is False """)
        result = self.search_cursor.fetchall()
        print(type(result))
        for rec in result:
            print(rec["filename"])

        req = {"text" : result[0]["extracted_text"]}
        x = requests.post(url, json = req)
        print(x.text)
        
        return

        # input_file_list = os.listdir(self.source_dir)
        # process_file_list = {} 
        # for file in input_file_list:
        #     log.info("Processing file %s ", file)
        #     file_sha = self.getSha512(self.source_dir +"/" +file)
        #     # check if file sha already exist in DB
        #     self.search_cursor.execute("""select * from "semantic-search".corpus where file_hash=%s """, (file_sha,))
        #     res = self.search_cursor.fetchone()
        #     if res is None:
        #         process_file_list[file_sha] = self.source_dir+"/"+file
        #     else:
        #         log.info("File %s already processed. Skipping.", file)
        
        
        # if not process_file_list:
        #     log.info("Nothing to process...")
        #     return
        
        # start_time = datetime.now()
        # futures = [self.doTextExtract.remote(hash=hash, file=file) for hash, file in process_file_list.items()]
        # book_text = ray.get(futures)
        # end_time = datetime.now()
        # # print(type(book_text))

        # text_extraction_time = end_time - start_time
        # log.info("Time taken to extract %d files: %d ", len(process_file_list), text_extraction_time.microseconds/1000)

        # for book in book_text:
        #     self.search_cursor.execute("""INSERT INTO "semantic-search".corpus \
        #         (filename, path, text_extract_time_ms, file_hash, extracted_text )\
        #         VALUES(%s, %s, %s, %s, %s)""", \
        #             (book["file"], self.source_dir, book["time"].microseconds/1000, book["hash"], book["extracted_text"]))
        
        # # TODO: cleanup file
        # for file in input_file_list:
        #     self.doFileCleanup(self.source_dir+"/"+file)

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

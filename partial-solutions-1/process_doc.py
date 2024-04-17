import os
import sys
import shutil
import psycopg2
import logging as log
import logging.config
import argparse
from datetime import datetime, timezone
from logging.handlers import SysLogHandler
from logging import FileHandler
import hashlib

from svlearn.text import TextExtraction, ChunkText, SentenceEncoder
from svlearn.config import ConfigurationMixin

log.basicConfig(format='%(asctime)s - %(filename)s:%(lineno)d %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(SysLogHandler('/dev/log'))

class ProcessDocument:
    def __init__(self, config) -> None:
        print("Processing documents...")
        print(config['database'])
        search_schema = config['database']['search-schema']
        user = config['database']['username']
        password = config['database']['password']
        host = config['database']['server']
        port = config['database']['port']
        self.source_dir = config['documents']['source-dir']
        self.destination_dir = config['documents']['destination-dir']

        self.search_conn = psycopg2.connect( database=search_schema, user=user, password=password, host=host, port=port)
        self.search_conn.autocommit = True
        self.search_cursor = self.search_conn.cursor()
        
    def __del__(self):
        #Closing the connection
        self.search_conn.close()
        print("Done Processing documents...")
        
        
    def postgres_connect(self):

        #Executing an MYSQL function using the execute() method
        self.search_cursor.execute("select version()")

        # Fetch a single row using fetchone() method.
        data = self.search_cursor.fetchone()
        print("Connection established to: ",data)

    def doFileCleanup(self, file):
        # Once the processing is done, move file to destination folder
        try:
            if os.path.exists(self.source_dir+"/"+file):
                os.remove(self.source_dir+"/"+file)
            shutil.move(self.source_dir+"/"+file,self.destination_dir)
        except Exception as e:
            errStr = str(e) 
            log.error(errStr)
    
    def getSha256(self, file):
        with open(self.source_dir+"/"+file, "rb") as f:
            digest = hashlib.file_digest(f, "sha256")
        return digest.hexdigest()
            
    def process(self):

        print(os.listdir("to-be-processed"))
        src_dir = config["documents"]["source-dir"]
        file_list = os.listdir(src_dir)
        dt = datetime.now(timezone.utc)
        for file in file_list:
            sha256 = self.getSha256(file)
            # doc_type = TextExtraction(src_dir+"/"+file).doctype_
            # print(doc_type)
            start_time = datetime.now()
            te = TextExtraction(src_dir+"/"+file).text_
            end_time = datetime.now()
            text_extraction_time = end_time - start_time
            print("Time taken to extract: ", text_extraction_time.microseconds)

            ct = ChunkText(config)
            start_time = datetime.now()
            chunks = ct.create_chunks(te)
            end_time = datetime.now()
            chunk_time = end_time - start_time
            print(len(chunks))
            print("Time taken to chunk: ", chunk_time.seconds)

            # print(chunks)
            se = SentenceEncoder(config)
            start_time = datetime.now()
            encoded_list = se.encode(chunks)
            end_time = datetime.now()
            encode_time = end_time - start_time
            print("Time taken to encode: ", encode_time.seconds)
            print(encoded_list.shape)

            print(type(text_extraction_time.microseconds))
            self.search_cursor.execute("""INSERT INTO "semantic-search".corpus \
                (filename, path, processed_time, text_extract_time_ms, chunk_time_sec, encode_time_sec, file_hash, extracted_text)\
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""", \
                    (file, src_dir, dt, text_extraction_time.microseconds, chunk_time.seconds, encode_time.seconds, sha256, te))

            # print(type(chunk_vector))
            # self.doFileCleanup(file)
            chunk_vector = [(i,  j) for i, j in zip(chunks, encoded_list)]
            print(chunk_vector[0])
            print("**********************************")
            print(chunk_vector[1][1])
            print(type(chunk_vector[1][1]))
            # chunk_vector = (chunks, encoded_list)

if __name__ == '__main__':
    mixin = ConfigurationMixin()
    config = mixin.load_config('bootcamp-config-ssv.yaml')
    pd = ProcessDocument(config)
    # pd.postgres_connect()
    pd.process()
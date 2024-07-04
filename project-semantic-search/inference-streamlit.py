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

import streamlit as st

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

st. title("Ask me anything about Amrtastakam")
# Create the main container
main_container = st.container()
with main_container:
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

    # Create a rectangular box for the text input field
    with st.expander(label="User Query"):
        user_query = st.text_input(key="user_text", placeholder="Type something...", label="")
        submit_button = st.button(label="Submit")
        if submit_button:
            query_embedding = inf.sentence_encoder.encode([user_query])

            fs = FaissIndexer(config)
            index = fs.load_index()
            #print(index.search(query_embedding, 5))
            D, I = index.search(query_embedding, 5)
            index_str_list = re.findall(r'\d+', str(I))
            #print(index_str_list)

            inf.search_cursor.execute("""SELECT max(id) from "semantic-search".corpus""")
            fid = inf.search_cursor.fetchone()["max"]
            fids = '"'+str(fid)+'"'
             
            llm_query = ""
            query = """SELECT chunk_text from "semantic-chunks"."""+fids+""" WHERE id = %s"""
            for idx, i_str in enumerate(index_str_list):
                i = int(i_str)
                inf.chunk_cursor.execute(query, (i,))
                publisher_records = inf.chunk_cursor.fetchall()
                temp_dict = {}
                temp_dict = publisher_records[0] 
                #st.write(idx+1, temp_dict["chunk_text"])
                if (idx == 0):
                    llm_query1 = temp_dict["chunk_text"]
                    llm_query = llm_query1 + " " + query 
                    #llm_query = llm_query1 + ". Summarize above statement based on " + query 

            #https://github.com/ollama/ollama/blob/main/docs/api.md
            #st.write("\n...LLM Response...\n")
            url = 'http://localhost:11434/api/generate'
            myobj = {"model": "llama3", "prompt": llm_query, "stream": False}
            x = requests.post(url, json = myobj)
            y = json.loads(x.text)
            st.write(y['response'])

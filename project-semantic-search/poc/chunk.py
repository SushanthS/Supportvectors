import sys
import os
import spacy
import time
import torch
import sqlite3
import pickle
import numpy as np
import pandas as pd
from loguru import logger
from sentence_transformers import SentenceTransformer
from filemanager import Filemanager
# use tika to read multiple file formats. tika needs Java Runtime 7+.
import tika
from tika_read import tika_read_content
#import const

MODEL = 'sentence-transformers/all-mpnet-base-v2'
NLP_MODEL = 'en_core_web_sm'
CHUNK_SIZE = 512
def is_non_empty_file(filepath):
    return os.path.isfile(filepath) and os.path.getsize(filepath) > 0
"""
#setting log level

The following are the supported levels ordered in increasing severity:
TRACE(5): low-level details of the program's logic flow.
DEBUG(10): Information that is helpful during debugging.
INFO(20): Confirmation that the application is behaving as expected.
SUCCESS(25): Indicates an operation was successful.
WARNING(30): Indicates an issue that may disrupt the application in the future.
ERROR(40): An issue that needs your immediate attention but won't terminate the program.
CRITICAL(50): A severe issue that can terminate the program, like "running out of memory".
Loguru defaults to DEBUG as minimum level
"""
LOG_LEVEL = "DEBUG"     # modify this to change log level

logger.remove(0)
logger.add(sys.stdout, level=LOG_LEVEL)

#PATH = "books"
EMBEDDING_FILE = "embeddings.pkl"
db_connection = sqlite3.connect("semantic-search.sqlite")
embedder = SentenceTransformer(MODEL)
#nlp = spacy.load('en_core_web_sm')
nlp = spacy.load(NLP_MODEL)

"""
#file_list = [f"{PATH}/pgThePioneer.txt"]
file_list = [f"{PATH}/houn2.txt",
            f"{PATH}/advofsh.txt",
            f"{PATH}/case.txt",
            f"{PATH}/lstb.txt",
            f"{PATH}/memoirsofsh.txt",
            f"{PATH}/retnofsh.txt",
            f"{PATH}/sign.txt",
            f"{PATH}/stud.txt",
            f"{PATH}/vall.txt",
            f"{PATH}/pgThePioneer.txt",
            f"{PATH}/BERT paper.pdf"]
"""

# sentences is a list string that will store the semantically separated strings
logger.info("processing corpus files")
start_time = time.time()
len_sentence_arr = np.array([])
len_above_threshold = 0
'''
cursor = db_connection.cursor()
for file in file_list:
    logger.info(f"\tprocessing {file}")
    cursor.execute("SELECT id FROM corpus WHERE file_name = ?", (file,))
    db_result = cursor.fetchone()
#    print(db_result)
    logger.info(f"\tdb_result: {db_result}")

    if db_result is not None:
#        print('File already processed: %s %s'%(file,db_result[0]))
        logger.info(f"\tFile {file} already processed: {db_result[0]}")
        continue

#    with open(file) as f:
#        in_text = f.read()
    in_text = tika_read_content(file)
    doc = nlp(in_text)
    temp_sent = list(doc.sents)
    for sentence in temp_sent:
        sentences.append(sentence.text)
        len_s = len(sentence.text)
        len_sentence_arr = np.append(len_sentence_arr, len_s)
        if len_s > CHUNK_SIZE:
            len_above_threshold += 1

    values = (file, PATH)
    cursor.execute('insert into corpus (file_name, file_path, process_time) values (?,?, CURRENT_TIMESTAMP)', values)
'''
filemanager = Filemanager(logger)
sentences = filemanager.process()
logger.info(f"done processing corpus files, time taken: {time.time() - start_time} seconds")

answer_table = pd.read_sql("select * from corpus", db_connection)
print(answer_table)

"""
len_sent = []
len_sent.append(0)
len_above_threshold = 0
embed_sentences = []
for sentence in sentences:
    len_sent.append(len(sentence))
#    embed_sentences.append(sentence)
    if len(sentence) > CHUNK_SIZE:
        len_above_threshold += 1

logger.info(f"\tnumber of sentences: {len(sentences)}")
logger.info(f"\tmin len: {np.min(len_sentence_arr)}")
logger.info(f"\tmax len: {np.max(len_sentence_arr)}")
logger.info(f"\tmean len: {np.mean(len_sentence_arr)}")
logger.info(f"\tlen above threshold: {len_above_threshold}")
#input("hit any key to continue...")
"""

logger.info("embedding sentences")
start_time = time.time()
embeddings = embedder.encode(sentences, convert_to_tensor=True)
#embeddings = sentence_embedder(MODEL, chunked_sentences)
logger.info(f"done embedding chunked sentences. time taken: {time.time() - start_time} seconds")
logger.info(f"embedding shape: {embeddings.shape}")

stored_data = {}
if is_non_empty_file(EMBEDDING_FILE):
    # Load sentences & embeddings from disc
    with open(EMBEDDING_FILE, "rb") as fIn:
        stored_data = pickle.load(fIn)
        print(type(stored_data))
        stored_sentences = stored_data["sentences"]
        stored_embeddings = stored_data["embeddings"]

    print("Before ", len(stored_data["embeddings"]), len(stored_embeddings))
    sentences.append(stored_data["sentences"])
    embeddings = torch.cat((embeddings, stored_data["embeddings"]), 0)
    print("After ", len(stored_data["embeddings"]), len(stored_embeddings))
# Store sentences & embeddings on disc
with open(EMBEDDING_FILE, "wb") as fOut:
    pickle.dump({"sentences": sentences, "embeddings": embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

db_connection.commit()
# you also need to close  the connection
db_connection.close()


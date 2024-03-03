import sys
import spacy
import time
import sqlite3
import pickle
import pandas as pd
from loguru import logger
from sentence_transformers import SentenceTransformer
# use tika to read multiple file formats. tika needs Java Runtime 7+.
import tika
from tika_read import tika_read_content

MODEL = 'sentence-transformers/all-mpnet-base-v2'
CHUNK_SIZE = 512
#setting log level
"""
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

PATH = "books"
db_connection = sqlite3.connect("semantic-search.sqlite")
embedder = SentenceTransformer(MODEL)
nlp = spacy.load('en_core_web_sm')

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
            f"{PATH}/pgThePioneer.txt"]

# sentences is a list string that will store the semantically separated strings
sentences = []
logger.info("processing corpus files")
cursor = db_connection.cursor()
start_time = time.time()
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

    values = (file, PATH)
    cursor.execute('insert into corpus (file_name, file_path, process_time) values (?,?, CURRENT_TIMESTAMP)', values)

logger.info(f"done processing corpus files, time taken: {time.time() - start_time} seconds")

answer_table = pd.read_sql("select * from corpus", db_connection)
print(answer_table)

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
logger.info(f"\tmin len: {min(len_sent)}")
logger.info(f"\tmax len: {max(len_sent)}")
logger.info(f"\tavg len: {sum(len_sent) / len(len_sent)}")
logger.info(f"\tlen above threshold: {len_above_threshold}")
#input("hit any key to continue...")

logger.info("embedding sentences")
start_time = time.time()
embeddings = embedder.encode(sentences, convert_to_tensor=True)
#embeddings = sentence_embedder(MODEL, chunked_sentences)
logger.info(f"done embedding chunked sentences. time taken: {time.time() - start_time} seconds")
logger.info(f"embedding shape: {embeddings.shape}")

# Store sentences & embeddings on disc
with open("embeddings.pkl", "wb") as fOut:
    pickle.dump({"sentences": sentences, "embeddings": embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

db_connection.commit()
# you also need to close  the connection
db_connection.close()


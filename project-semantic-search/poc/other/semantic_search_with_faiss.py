import sys
import spacy
import time
import faiss
import re
from loguru import logger
from sentence_transformers import SentenceTransformer

# use tika to read multiple file formats. tika needs Java Runtime 7+.
import tika
from tika_read import tika_read_content


#sys.path.append('/Users/maheshsrinivas/anaconda3/lib/python3.11/site-packages/faiss')

MODEL = 'sentence-transformers/all-mpnet-base-v2'
CHUNK_SIZE = 512
PATH = "/Users/maheshsrinivas/Documents/LLM Bootcamp 2024/TextFiles"

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

embedder = SentenceTransformer(MODEL)

nlp = spacy.load('en_core_web_sm')
#nlp = spacy.load('en')

file_list = [f"{PATH}/houn2.txt",
             f"{PATH}/advofsh.txt",
             f"{PATH}/case.txt",
             f"{PATH}/lstb.txt",
             f"{PATH}/memoirsofsh.txt",
             f"{PATH}/retnofsh.txt",
             f"{PATH}/sign.txt",
             f"{PATH}/stud.txt",
             f"{PATH}/vall.txt"]

# sentences is a list string that will store the semantically separated strings
sentences = []
logger.info("processing corpus files")
start_time = time.time()
for file in file_list:
    logger.info(f"\tprocessing {file}")
    try:
        f = open(file)
    except FileNotFoundError:
        logger.error(f"File {file} not found! Skipping file")
        continue
    else:
        f.close()
        in_text = tika_read_content(file)
    doc = nlp(in_text)
    temp_sent = list(doc.sents)
    for sentence in temp_sent:
        sentences.append(sentence.text)
logger.info(f"done processing corpus files, time taken: {time.time() - start_time} seconds")

len_sent = []
len_above_threshold = 0
embed_sentences = []
for sentence in sentences:
    len_sent.append(len(sentence))
#    embed_sentences.append(sentence)
    if len(sentence) > CHUNK_SIZE:
        len_above_threshold += 1

logger.info(f"\tlen sentences: {len(sentences)}")
logger.info(f"\tmin len: {min(len_sent)}")
logger.info(f"\tmax len: {max(len_sent)}")
logger.info(f"\tavg len: {sum(len_sent) / len(len_sent)}")
logger.info(f"\tlen above threshold: {len_above_threshold}")
#input("hit any key to continue...")

logger.info("embedding sentences")
start_time = time.time()
embeddings = embedder.encode(sentences)
#embeddings = sentence_embedder(MODEL, chunked_sentences)
logger.info(f"done embedding chunked sentences. time taken: {time.time() - start_time} seconds")
logger.info(f"embedding shape: {embeddings.shape}")

logger.info("moving vectors to faiss")
start_time = time.time()
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
logger.info(f"index trained?: {index.is_trained}")
index.add(embeddings)
logger.info(f"done indexing. time taken: {time.time() - start_time} seconds")
logger.info(f"\tindex.ntotal: {index.ntotal}")

k = 4
while True:
    query_text = input("prompt: > ")
    if query_text == 'quit':
        break
    logger.info("searching in faiss")
    start_time = time.time()
    query = embedder.encode([query_text])
    D, I = index.search(query, k)  # search
    logger.info(f"done searching in faiss time taken: {time.time() - start_time} seconds")

    index_str_list = re.findall(r'\d+', str(I))
    for i_str in index_str_list:
        i = int(i_str)
        print(f"Index: {i}\n {sentences[i]}")

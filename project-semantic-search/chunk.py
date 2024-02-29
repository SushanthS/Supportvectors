import spacy
import time
import sqlite3
import pickle
import pandas as pd
from sentence_transformers import SentenceTransformer


MODEL = 'sentence-transformers/all-mpnet-base-v2'
CHUNK_SIZE = 512

PATH = "books"
db_connection = sqlite3.connect("semantic-search.sqlite")

embedder = SentenceTransformer(MODEL)

nlp = spacy.load('en_core_web_sm')

file_list = [f"{PATH}/pgThePioneer.txt"]
# file_list = [f"{PATH}/houn2.txt",
            #  f"{PATH}/advofsh.txt",
            #  f"{PATH}/case.txt",
            #  f"{PATH}/lstb.txt",
            #  f"{PATH}/memoirsofsh.txt",
            #  f"{PATH}/retnofsh.txt",
            #  f"{PATH}/sign.txt",
            #  f"{PATH}/stud.txt",
            #  f"{PATH}/vall.txt"]

# sentences is a list string that will store the semantically separated strings
sentences = []
print("processing corpus files")
start_time = time.time()
for file in file_list:
    print(f"\tprocessing {file}")
    with open(file) as f:
        in_text = f.read()
    doc = nlp(in_text)
    temp_sent = list(doc.sents)
    for sentence in temp_sent:
        sentences.append(sentence.text)

print(f"done processing corpus files, time taken: {time.time() - start_time} seconds")

c = db_connection.cursor()
values = (file, PATH)
c.execute('insert into corpus (file_name, file_path, process_time) values (?,?, CURRENT_TIMESTAMP)', values)

answer_table = pd.read_sql("select * from corpus", db_connection)
print(answer_table)

len_sent = []
len_above_threshold = 0
embed_sentences = []
for sentence in sentences:
    len_sent.append(len(sentence))
#    embed_sentences.append(sentence)
    if len(sentence) > CHUNK_SIZE:
        len_above_threshold += 1

print("\tlen sentences: ", len(sentences))
print("\tmin len: ", min(len_sent))
print("\tmax len: ", max(len_sent))
print("\tavg len: ", sum(len_sent) / len(len_sent))
print("\tlen above threshold: ", len_above_threshold)
#input("hit any key to continue...")

print("embedding sentences")
start_time = time.time()
embeddings = embedder.encode(sentences, convert_to_tensor=True)
#embeddings = sentence_embedder(MODEL, chunked_sentences)
print(f"done embedding chunked sentences. time taken: {time.time() - start_time} seconds")
print("embedding shape: ", embeddings.shape)

# Store sentences & embeddings on disc
with open("embeddings.pkl", "wb") as fOut:
    pickle.dump({"sentences": sentences, "embeddings": embeddings}, fOut, protocol=pickle.HIGHEST_PROTOCOL)

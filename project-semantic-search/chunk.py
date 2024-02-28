import spacy
import time
from sentence_transformers import SentenceTransformer

MODEL = 'sentence-transformers/all-mpnet-base-v2'
CHUNK_SIZE = 512

PATH = "books"

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
for file in file_list:
    print(f"processing {file}")
    start_time = time.time()
    with open(file) as f:
        in_text = f.read()
    doc = nlp(in_text)
    temp_sent = list(doc.sents)
    for sentence in temp_sent:
        sentences.append(sentence.text)
    print(f"processed file {file}, time taken: {time.time() - start_time} seconds")
print("done processing corpus files")

#print("sentences: ", sentences)

chunked_sentences = []
chunked_sentence = ""

print("chunking sentences")
start_time = time.time()
for sentence in sentences:
#    print("sentence: ", sentence, "type: ", type(sentence))
    if len(sentence) + len(chunked_sentence) < CHUNK_SIZE:
        chunked_sentence += sentence
    else:
        chunked_sentences.append(chunked_sentence)
        chunked_sentence = sentence

print(f"done chunking sentences. time taken: {time.time() - start_time} seconds")

print("embedding chunked sentences")
start_time = time.time()
embeddings = embedder.encode(chunked_sentences, convert_to_tensor=True)
print(f"done embedding chunked sentences. time taken: {time.time() - start_time} seconds")
print("embedding shape: ", embeddings.shape)

while True:
    query_text = input("prompt: > ")
    if query_text == 'quit':
        break
    query = embedder.encode(query_text, convert_to_tensor=True)

    from sentence_transformers import util
    search_results = util.semantic_search(query, embeddings, top_k = 3)
#    search_results

    for index, result in enumerate(search_results[0]):
        print('-'*80)
        print(f'Search Rank: {index}, Relevance score: {result["score"]} ')
        print(sentences[result['corpus_id']])
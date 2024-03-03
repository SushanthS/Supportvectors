
import pickle
import time
from loguru import logger

from sentence_transformers import SentenceTransformer


MODEL = 'sentence-transformers/all-mpnet-base-v2'


embedder = SentenceTransformer(MODEL)


# Load sentences & embeddings from disc
with open("embeddings.pkl", "rb") as fIn:
    stored_data = pickle.load(fIn)
    stored_sentences = stored_data["sentences"]
    stored_embeddings = stored_data["embeddings"]

while True:
    query_text = input("prompt: > ")
    if query_text == 'quit':
        break
    query = embedder.encode(query_text, convert_to_tensor=True)

    from sentence_transformers import util
    logger.info("searching...")
    start_time = time.time()
    search_results = util.semantic_search(query, stored_embeddings, top_k = 4)
    logger.info(f"done searching, time taken: {time.time() - start_time} seconds")
    print(search_results)

#    input("hit any key to continue...")

    for index, result in enumerate(search_results[0]):
        print('-'*80)
        print(f'Search Rank: {index}, Relevance score: {result["score"]} ')
        print('result[corpus_id]:', result['corpus_id'])
#        input("hit any key to continue...")
        print(stored_sentences[result['corpus_id']])

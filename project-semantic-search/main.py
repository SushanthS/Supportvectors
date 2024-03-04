import sys
import pickle
from loguru import logger
from flask import Flask, jsonify, Response, request
import json

#Internal modules
from filemanager import Filemanager
#from transformer import Transformer
#from vectordb import VectorDB
import const
from sentence_transformers import SentenceTransformer
from sentence_transformers import util

embedder = SentenceTransformer(const.MODEL)
logger.remove(0)
logger.add(sys.stdout, level=const.LOG_LEVEL)
# Load sentences & embeddings from disc
with open("embeddings.pkl", "rb") as fIn:
    stored_data = pickle.load(fIn)
    stored_sentences = stored_data["sentences"]
    stored_embeddings = stored_data["embeddings"]


'''
vectordb = VectorDB(logger, embeddings)
vectordb.indexing()
'''

# API handler to process queries
def querylookup():
    print(request.get_json()['query'])
    query_text = request.get_json()['query']
    print("query_text", query_text)
    query = embedder.encode(query_text, convert_to_tensor=True)
    #index_str_list = vectordb.search(query, const.TOP_K)  # search
    search_results = util.semantic_search(query, stored_embeddings, top_k=4)
    output = []
    for index, result in enumerate(search_results[0]):
        print('-' * 80)
        print(f'Search Rank: {index}, Relevance score: {result["score"]} ')
        print('result[corpus_id]:', result['corpus_id'])
        #        input("hit any key to continue...")
        print(stored_sentences[result['corpus_id']])
        output.append(stored_sentences[result['corpus_id']])

    print(output)
    return output

def main():
    # Initialize api server
    app = Flask("SemanticSearch")
    app.add_url_rule("/query", "query", querylookup, methods=['POST'])
    app.run(port=9909)

if __name__ == '__main__':
    main()

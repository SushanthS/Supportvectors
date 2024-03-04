
import json
import pickle

import logging
import logging.config
from logging.handlers import SysLogHandler
from logging import FileHandler


from sentence_transformers import SentenceTransformer, util


# MODEL = 'sentence-transformers/all-mpnet-base-v2'


# embedder = SentenceTransformer(MODEL)


# # Load sentences & embeddings from disc
# with open("embeddings.pkl", "rb") as fIn:
#     stored_data = pickle.load(fIn)
#     stored_sentences = stored_data["sentences"]
#     stored_embeddings = stored_data["embeddings"]

# while True:
#     query_text = input("prompt: > ")
#     if query_text == 'quit':
#         break
#     query = embedder.encode(query_text, convert_to_tensor=True)

#     from sentence_transformers import util
#     search_results = util.semantic_search(query, stored_embeddings, top_k = 3)
#     print(search_results)

# #    input("hit any key to continue...")

#     for index, result in enumerate(search_results[0]):
#         print('-'*80)
#         print(f'Search Rank: {index}, Relevance score: {result["score"]} ')
#         print('result[corpus_id]:', result['corpus_id'])
# #        input("hit any key to continue...")
#         print(stored_sentences[result['corpus_id']])


SEMANTIC_SEARCH_VERSION = 0.1

class SSearchVersion:
    def __init__(self):
        self.name = "Semantic Search Server"
        self.version = SEMANTIC_SEARCH_VERSION

class SSearchLogger:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s - [%(module)s] - %(filename)s:%(lineno)d - %(message)s',level=logging.INFO)
        self.logger = logging.getLogger("SSearch")
        # self.logger.addHandler(SysLogHandler('/dev/log'))
        self.logger.addHandler(FileHandler('SSearchServer.log'))

        # Set Logger level to DEBUG for debugging.  Production should run in INFO
        self.logger.setLevel(logging.INFO)

    def getLogger(self):
        return self.logger

class SSearchData:
    def __init__(self):
        pass

class SSearch(object):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SSearch, cls).__new__(cls)

        # Put any initialization here.
        MODEL = 'sentence-transformers/all-mpnet-base-v2'
        embedder = SentenceTransformer(MODEL)

        # Load sentences & embeddings from disc
        with open("embeddings.pkl", "rb") as fIn:
            stored_data = pickle.load(fIn)
            stored_sentences = stored_data["sentences"]
            stored_embeddings = stored_data["embeddings"]
        
        return cls._instance
    
    def __init__(self):
        pass


    def doSearch(self, query):
        equery = self.embedder.encode(query, convert_to_tensor=True)

        search_results = util.semantic_search(equery, self.stored_embeddings, top_k = 3)
        print(search_results)

        return json.dumps(search_results[0].__dict__, default=lambda o: o.__dict__) 

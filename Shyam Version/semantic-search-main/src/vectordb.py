import faiss
import re

#internal module
import const

class VectorDB:
    def __init__(self, logger, embeddings):
        self.logger = logger
        self.embeddings = embeddings
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        return
    
    def indexing(self):
        self.logger.info("Indexing vectors")
        self.index.add(self.embeddings)
        self.logger.debug(f"\tindex.ntotal: {self.index.ntotal}")
        return
    
    def search(self, query, k):
        self.logger.debug("Searcing vectorDB")
        D, I = self.index.search(query, k)
        index_str_list = re.findall(r'\d+', str(I))
        return index_str_list
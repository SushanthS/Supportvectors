import sys
import time
from sentence_transformers import SentenceTransformer
from loguru import logger

#internal module
import const

class Transformer(object):
    def __init__(self, logger):
        self.logger = logger
        self.embedder =  SentenceTransformer(const.MODEL)
        return
    def embed(self, sentences):
        self.logger.info("Embedding sentences")
        start_time = time.time()
        embeddings = self.embedder.encode(sentences)
        self.logger.debug(f"done embedding chunked sentences. time taken: {time.time() - start_time} seconds")
        self.logger.debug(f"embedding shape: {embeddings.shape}")
        return embeddings
    def process(self, sentences):
        embeddings = self.embed(sentences)
        return embeddings
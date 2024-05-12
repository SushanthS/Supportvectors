import logging as log
from logging.handlers import SysLogHandler
import faiss
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from svlearn.config import ConfigurationMixin

VERSION="0.1"
class faissindexer:
    def __init__(self):
        pass

    async def __call__(self, request):
        pass

class FaissIndexer:
    def __init__(self, config):
        search_schema = config['database']['search-schema']
        # chunk_schema = config['database']['chunk-schema']
        user = config['database']['username']
        password = config['database']['password']
        host = config['database']['server']
        port = config['database']['port']
        self.source_dir = config['documents']['source-dir']
        self.destination_dir = config['documents']['destination-dir']

        # Connection for search schema
        self.search_conn = psycopg2.connect(database=search_schema, user=user, password=password, host=host, port=port)
        self.search_conn.autocommit = True
        self.search_cursor = self.search_conn.cursor(cursor_factory=RealDictCursor)

        # Separate connection for chunk schema.
        self.chunk_conn = psycopg2.connect(dbname=search_schema, user=user, password=password, host=host, port=port)
        self.chunk_conn.autocommit = False
        self.chunk_cursor = self.chunk_conn.cursor(cursor_factory=RealDictCursor)

    async def __call__(self, request):
        pass

    # TODO for all chunk table
    def embedding_to_vectorDB(self):
        self.chunk_cursor.execute("""SELECT chunk_encoded, id from "semantic-chunks".33;""" )
        result = self.fetchall()
        id_vectors_tuple_list = []
        for i in range(0, len(result)):
            recreated_scaler_from_bytes = np.frombuffer(result[i][0], dtype='float32')
            recreated_vector_from_bytes = np.reshape(recreated_scaler_from_bytes, (1,512))
            id_vectors_tuple_list.append((result[i][1],recreated_vector_from_bytes))
            log.debug(f'recreated vector shape -> {recreated_vector_from_bytes.shape}')
        vectors = []
        ids = []
        for id_vector_tuple  in id_vectors_tuple_list:
            ids.append(id_vector_tuple[0])
            vectors.append(id_vector_tuple[1])
        ids = np.array(ids)
        vectors = np.vstack(vectors).astype('float32')

        base_index = faiss.IndexFlatL2(512)
        index = faiss.IndexIDMap(base_index)
        index.add_with_ids(vectors, ids)
        return index


if __name__ == '__main__':
    config_file = "bootcamp-config-ssv.yaml"

    parser = argparse.ArgumentParser(description='Text Extractor Process')
    parser.add_argument('-c','--config', help='Config file', required=False)
    parser.add_argument('-V','--version', action='version', version='%(prog)s '+VERSION)
    args = parser.parse_args()

    if args.config is not None:
        config_file = args.config

    mixin = ConfigurationMixin()
    config = mixin.load_config(config_file)

    fs = FaissIndexer(config)
    fs.embedding_to_vectorDB()
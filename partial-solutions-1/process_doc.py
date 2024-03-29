import sys
from datetime import datetime
from svlearn.text import TextExtraction, ChunkText, SentenceEncoder
from svlearn.config import ConfigurationMixin
import psycopg2


class ProcessDocument:
    def __init__(self, config) -> None:
        print("Processing documents...")
        print(config['database'])
        search_schema = config['database']['search-schema']
        user = config['database']['username']
        password = config['database']['password']
        host = config['database']['server']
        port = config['database']['port']

        self.search_conn = psycopg2.connect( database=search_schema, user=user, password=password, host=host, port=port)
        self.search_cursor = self.search_conn.cursor()
        
    def __del__(self):
        #Closing the connection
        self.search_conn.close()
        print("Done Processing documents...")
        
        
    def postgres_connect(self):

        #Executing an MYSQL function using the execute() method
        self.search_cursor.execute("select version()")

        # Fetch a single row using fetchone() method.
        data = self.search_cursor.fetchone()
        print("Connection established to: ",data)


print("processing docs...")
if __name__ == '__main__':
    mixin = ConfigurationMixin()
    config = mixin.load_config('bootcamp-config-ssv.yaml')
    pd = ProcessDocument(config)
    pd.postgres_connect()
    sys.exit()
    start_time = datetime.now()
    te = TextExtraction("../project-semantic-search/books/BERT paper.pdf").to_text("../project-semantic-search/books/BERT paper.pdf")
    end_time = datetime.now()
    text_extraction_time = end_time - start_time
    print("Time taken to extract: ", text_extraction_time.microseconds)

    ct = ChunkText()
    start_time = datetime.now()
    chunks = ct.create_chunks(te)
    end_time = datetime.now()
    chunk_time = end_time - start_time
    print(len(chunks))
    print("Time taken to chunk: ", chunk_time.seconds)

    # print(chunks)
    se = SentenceEncoder()
    start_time = datetime.now()
    encoded_list = se.encode(chunks)
    end_time = datetime.now()
    encode_time = end_time - start_time
    print("Time taken to encode: ", encode_time.seconds)
    print(encoded_list.shape)

    chunk_vector = [(i,  j) for i, j in zip(chunks, encoded_list)]
    # chunk_vector = (chunks, encoded_list)
    print(chunk_vector[0])

    print(type(chunk_vector))

    # print(encoded_list)
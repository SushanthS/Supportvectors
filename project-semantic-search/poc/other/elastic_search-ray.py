from text_extractor import *
from text_chunker import *
from sentence_encoder import *
from faiss_indexer import *
import psycopg
import faiss
import sys
import numpy as np
import ray
import time
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM
import torch
from elasticsearch import Elasticsearch
es = Elasticsearch("https://81324f3d6779418c830f5825bc0b7cdf.us-central1.gcp.cloud.es.io:443",
                    api_key="c1VWd0lvOEJGaFZwZ29nNUQ2eGs6bTBlMldoLWdRT0NIaXpqM202akY5UQ==")
print(es.info())
if es.indices.exists(index="semantic_search"):
    es.indices.delete(index='semantic_search')
es.indices.create(index='semantic_search')
es.indices.put_mapping(index="semantic_search", 
                        body = {
                            "properties": {
                                "sentence": {
                                    "type": "text",
                                    "fields": {
                                        "keyword": {
                                            "type": "keyword",
                                            "ignore_above": 256
                                        }
                                    }
                                }
                            }
                        })
#cloudid = "8d9e623461974c8e92b00c709db2b7dd:dXMtY2VudHJhbDEuZ2NwLmNsb3VkLmVzLmlvJDgxMzI0ZjNkNjc3OTQxOGM4MzBmNTgyNWJjMGI3Y2RmJDM5ZjE2Njk3YzhhYjQ0ZGE4Y2NkYmE5MWUzOGY5MjZk"
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = torch.device('mps')
#Note: TODO Flush GPU

sys.path.append(os.path.abspath("/Users/shyam.govindaraj/Downloads/partial-solutions-1"))
directory = "/Users/shyam.govindaraj/Downloads/pdf"

#comment 
def connectDB():
    conn = psycopg.connect(host='127.0.0.1', 
                    dbname='shyam.govindaraj', 
                    user='shyam.govindaraj', 
                    password='testing123', 
                    port=5433)
    cursor = conn.cursor()
    return conn, cursor

def create_tables():
    conn, cursor = connectDB() 
    cursor.execute("""
        DROP TABLE IF EXISTS chunks;
                """)  
    cursor.execute("""
            DROP TABLE IF EXISTS files;
                   """)  
    cursor.execute("""
        DROP EXTENSION IF EXISTS vector;
                """)  
    cursor.execute("""
        CREATE EXTENSION vector;
                """)    
    cursor.execute("""
            CREATE TABLE files (
                fileid serial PRIMARY KEY,
                name text,
                type text,
                data text)
            """)
    cursor.execute("""
            CREATE TABLE chunks (
                chunkid serial PRIMARY KEY,
                data text,
                embedding bytea,
                fileid integer)
            """)
    cursor.execute("""
            ALTER TABLE chunks ADD FOREIGN KEY ("fileid") REFERENCES "files" ("fileid")
            """)
    conn.commit()
    conn.close()

@ray.remote
def convert_doc_to_text(file):
    text_list = []
    conn, cursor = connectDB() 
    print("Convert to text")

    fielname = os.path.basename(file)
    extract = TextExtraction.to_text(file)
    text_list.append(extract)

    query = """INSERT INTO files(name, type, data) VALUES(%s, %s, %s) RETURNING fileid;"""
    cursor.execute(query, (fielname, 'pdf', extract))
    id = cursor.fetchall()
    conn.commit()
    conn.close()
    return id

@ray.remote
def text_to_chunk(fileid):
    print("convert to chunks")
    conn, cursor = connectDB()
    query = """SELECT data from files WHERE fileid = %s""" #TODO Fix the query
    cursor.execute(query, ([fileid]))
    text_list = cursor.fetchall()

    chunked_text_list = []
    recordid_list = []
    ChText = ChunkText()
    es1 = Elasticsearch("https://81324f3d6779418c830f5825bc0b7cdf.us-central1.gcp.cloud.es.io:443",
                    api_key="c1VWd0lvOEJGaFZwZ29nNUQ2eGs6bTBlMldoLWdRT0NIaXpqM202akY5UQ==")
    for text_extract in text_list:
        text_chunks = ChText.create_chunks(text_extract[0])
        for text_chunk in text_chunks:
            doc = {"sentence": text_chunk}
            es1.index(index="semantic_search", document=doc)
            chunked_text_list.append(text_chunk)
            query = """INSERT INTO chunks(data, fileid)
                VALUES(%s, %s) RETURNING chunkid;"""
            cursor.execute(query, (text_chunk, fileid))  #TODO get ID from DB
            id = cursor.fetchone()[0]
            print(id)
            recordid_list.append(id)
    print(f"chunk size: {len(chunked_text_list)}, type chunked_text_list: {type(chunked_text_list)}")
    conn.commit()
    conn.close()
    return fileid

@ray.remote
def chunk_to_embedding(fileid):
#def chunk_to_embedding():
    conn, cursor = connectDB() 
    query = """SELECT data, chunkid from chunks WHERE fileid = %s;""" #TODO Fix the query
    cursor.execute(query, ([fileid]))
    #cursor.execute(query, ([1]))

    chunk_list = []
    id_list = []
    for record in cursor.fetchall():
        chunk, id = record
        chunk_list.append(chunk)
        id_list.append(id)

    sentence_encoder = SentenceEncoder()
    sentence_embedding = sentence_encoder.encode(chunk_list)
    print(f"dimension of sentence_embedding: {sentence_embedding.shape}")

    query = """UPDATE chunks SET embedding=%s WHERE chunkid = %s"""
    for idx, embedding in enumerate(sentence_embedding):
        cursor.execute(query,(embedding.tobytes(), id_list[idx]))
    conn.commit()
    conn.close()
    print(sentence_embedding.shape)
    return sentence_embedding

@ray.remote
def embedding_to_vectorDB(fileid):
    id_vectors_tuple_list = get_embeddings_from_chunk_db(fileid)
    vectors = []
    ids = []
    for id_vector_tuple  in id_vectors_tuple_list:
        ids.append(id_vector_tuple[0])
        vectors.append(id_vector_tuple[1])
    ids = np.array(ids)
    vectors = np.vstack(vectors).astype('float32')

    base_index = faiss.IndexFlatL2(512) #TODO extract this from embedding
    index = faiss.IndexIDMap(base_index)
    index.add_with_ids(vectors, ids)
    return index

def get_embeddings_from_chunk_db(fileid):
    conn, cursor = connectDB() 
    id_vectors_tuple_list = []
    query = 'SELECT embedding, chunkid FROM chunks WHERE fileid = %s'
    ids_vectors_from_db = cursor.execute(query, ([fileid])).fetchall()
    for i in range(0, len(ids_vectors_from_db)):
        recreated_scaler_from_bytes = np.frombuffer(ids_vectors_from_db[i][0], dtype='float32')
        recreated_vector_from_bytes = np.reshape(recreated_scaler_from_bytes, (1,512))
        id_vectors_tuple_list.append((ids_vectors_from_db[i][1],recreated_vector_from_bytes))
        log.debug(f'recreated vector shape -> {recreated_vector_from_bytes.shape}')
    return id_vectors_tuple_list

if __name__ == '__main__':

    # Initialize Ray
    ray.init()
    # Create Schema
    create_tables()

    # Get list of files in the directory
    file_list = []
    for filename in os.scandir(directory):
        if filename.is_file():
            print(filename.path)
            file_list.append(filename.path)

    # Convert doc to text 
    ray.get([convert_doc_to_text.remote(file) for file in file_list])
    
    # Convert text to chunk
    ray.get([text_to_chunk.remote(index+1) for index,_ in enumerate(file_list)])

    # Convert chunk to embedding 
    ray.get([chunk_to_embedding.remote(index+1) for index,_ in enumerate(file_list)])

    #model = AutoModelForCausalLM.from_pretrained(
    #"meta-llama/Llama-2-7b-chat-hf",
    #device_map='auto')

    #tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf",)
    #embedding to vector DB
    objs = ray.get([embedding_to_vectorDB.remote(index+1) for index,_ in enumerate(file_list)])
    index = objs[0]

    # Consumer pipeline - Process query
    conn, cursor = connectDB() 

    while True:
        user_query = input("Enter query:")
        print("user_query is: " + user_query)
        input_list = []
        sentence_encoder = SentenceEncoder()
        query_embedding = sentence_encoder.encode([user_query])
        D, I = index.search(query_embedding, 5)
        index_str_list = re.findall(r'\d+', str(I))
        query = """SELECT data from chunks WHERE chunkid = %s"""
        context = ""
        for idx, i_str in enumerate(index_str_list):
            i = int(i_str)
            cursor.execute(query, (i,))
            publisher_records = cursor.fetchall()
            print("output: ", i, publisher_records)
            print(type(publisher_records[0][0]))
            context = context + publisher_records[0][0] + "\n"
            input_list.append(publisher_records[0][0])
        conn.close()
        #query="Explain session layer"
        #print("QUERY: ", user_query)
        #print("RETRIEVED OUTPUT", context)

        # Elastic search integration
        body1 = {
            "from": 0,
            "size": 10,
            "query": {
                "match": {
                    "sentence": user_query
                }
            }
        }
        es1 = Elasticsearch("https://81324f3d6779418c830f5825bc0b7cdf.us-central1.gcp.cloud.es.io:443",
                    api_key="c1VWd0lvOEJGaFZwZ29nNUQ2eGs6bTBlMldoLWdRT0NIaXpqM202akY5UQ==")
        time.sleep(6)
        res = es1.search(index="semantic_search", body=body1)
        print("================\n")
        print(res)
        for item in res['hits']['hits']:
            if item['_source']['sentence'] not in input_list:
                input_list.append(item['_source']['sentence'])

        for item in input_list:
            print(item)


        # Cross encoder integration
        from sentence_transformers import CrossEncoder
        import numpy as np
        model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)

        sentence_combinations = [[user_query, sentence] for sentence in input_list]
        scores = model.predict(sentence_combinations)

        # Sort the scores in decreasing order to get the corpus indices
        ranked_indices = np.argsort(scores)[::-1]
        print("scores:", scores)
        print("indices:", ranked_indices)
        for i in range(len(ranked_indices)):
            print(input_list[i])

        #LLM Integration
        '''
        def get_llama2_chat_reponse(prompt, max_new_tokens=50):
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens, temperature= 0.00001)
            response = tokenizer.decode(outputs[0], skip_special_tokens=True)
            return response
    
        #prompt = f'''
        #[INST]
        #Give answer for the question strictly based on the context provided. Provide a detailed answer.

        #Question: {user_query}

        #Context : {context}
        #[/INST]
        '''
        prompt
        print(get_llama2_chat_reponse(prompt, max_new_tokens=500))
        '''

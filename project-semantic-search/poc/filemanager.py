import os
import time
import spacy
import const
import tika
from tika_read import tika_read_content
import numpy as np
import sqlite3

class Filemanager(object):
    def __init__(self, logger):
        self.file_location = const.PATH
        self.chunk_size = const.CHUNK_SIZE
        self.logger = logger
        self.nlp_model = const.NLP_MODEL
        self.db_connection = sqlite3.connect("semantic-search.sqlite")
        self.cursor = self.db_connection.cursor()

    def __del__(self):
        self.db_connection.commit()
        # you also need to close  the connection
        self.db_connection.close()

    # Convert docs to text
    def parse(self):
        return
    
    # Convert text files to chunks 
    def chunk(self):
        self.logger.info("Chunking sentences")
        sentences = []
        len_sentence_arr = np.array([])
        len_above_threshold = 0
        nlp = spacy.load(self.nlp_model)
        file_list = os.listdir(self.file_location)
        self.logger.info(file_list)
        start_time = time.time()
        for dirpath,_,filenames in os.walk(self.file_location):
            for file in filenames:
                filename = os.path.join(dirpath, file)
                self.cursor.execute("SELECT id FROM corpus WHERE file_name = ?", (filename,))
                db_result = self.cursor.fetchone()
                #    print(db_result)
                self.logger.info(f"\tdb_result: {db_result}")

                if db_result is not None:
                    #        print('File already processed: %s %s'%(file,db_result[0]))
                    self.logger.info(f"\tFile {file} already processed: {db_result[0]}")
                    continue
                self.logger.debug(f"\tprocessing {filename}")
                '''
                try:
                    f = open(filename)
                except FileNotFoundError:
                    self.logger.error(f"File {filename} not found! Skipping file")
                    continue
#                else:
#                    in_text = f.read()
'''
                in_text = tika_read_content(filename)
                doc = nlp(in_text)
                temp_sent = list(doc.sents)
                for sentence in temp_sent:
                    sentences.append(sentence.text)
                    len_s = len(sentence.text)
                    len_sentence_arr = np.append(len_sentence_arr, len_s)
                    if len_s > const.CHUNK_SIZE:
                        len_above_threshold += 1
                self.logger.debug(f"done processing corpus files, time taken: {time.time() - start_time} seconds")
                values = (filename, dirpath)
                self.cursor.execute('insert into corpus (file_name, file_path, process_time) values (?,?, CURRENT_TIMESTAMP)', values)

        len_sent = np.array([])
        len_above_threshold = 0
        embed_sentences = []
        for sentence in sentences:
            len_s = len(sentence)
            len_sent = np.append(len_sent, [len_s])
            if len_s > const.CHUNK_SIZE:
                len_above_threshold += 1

        self.logger.debug(f"len_sent[:5]: {len_sent[:5]}")
        self.logger.debug(f"\tlen sentences: {len(sentences)}")
        self.logger.debug(f"\tmin len: {min(len_sent)}")
        self.logger.debug(f"\tmax len: {max(len_sent)}")
        self.logger.debug(f"\tavg len: {sum(len_sent) / len(sentences)}")
        self.logger.debug(f"\tlen above threshold: {len_above_threshold}")

        return sentences
    
    def process(self):
        # Refer section 3.4.1 in project document
        self.parse()
        sentences = self.chunk()
        return sentences
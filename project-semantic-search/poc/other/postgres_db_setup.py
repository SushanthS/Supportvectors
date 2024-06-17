'''
sudo rm -rf /db/postgres/*
docker rm -f pgvector
docker run -itd -e POSTGRES_DB=semanticsearch -e POSTGRES_USER=semanticsearch -e POSTGRES_PASSWORD=semanticsearch -p 5432:5432 -v /db/postgres:/var/lib/postgresql/data --name pgvector ankane/pgvector:v0.3.1
PGPASSWORD=semanticsearch psql -h localhost -p 5432 -U semanticsearch
PGPASSWORD=semanticsearch psql -h localhost -p 5432 -U semanticsearch -c '\l' 
'''
import psycopg
import sys
import numpy as np
import time

#Note: TODO Flush GPU

def connectDB():
    conn = psycopg.connect(host='127.0.0.1', 
                    dbname='semanticsearch', 
                    user='semanticsearch', 
                    password='semanticsearch', 
                    port=5432)
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

if __name__ == '__main__':

    # Create schema
    create_tables()
    print("... done ...")

#  -------------------------------------------------------------------------------------------------
#   Copyright (c) 2023.  SupportVectors AI Lab
#   This code is part of the training material, and therefore part of the intellectual property.
#   It may not be reused or shared without the explicit, written permission of SupportVectors.
#  #
#   Use is limited to the duration and purpose of the training at SupportVectors.
#  #
#   Author: Asif Qamar
#  -------------------------------------------------------------------------------------------------
#
import logging as log

from typing import Optional

from sqlmodel import Field, Session, SQLModel, create_engine
import uuid
#
# This is an alternative way to load the wikipedia
# data. It uses the SQLModel library to create a DOCUMENT
# class, and then uses the SQLModel to load the data into
# the database.
#
# Currently, this is not used in the code, but it is
# provided as an example of how to use the SQLModel.
#
class DOCUMENT(SQLModel, table=True, schema='documents'):
    """SQLModel for the DOCUMENT table"""
    __tablename__ = 'DOCUMENT'
    ID: Optional[int] = Field(default=None, primary_key=True)
    TEXT: str
    PATH: str
    UUID: str
    LANGUAGE: Optional[str] = 'en-us'
    DOCTYPE: Optional[str] = 'text'
    CHUNKED: bool = False

if __name__ == '__main__':
    log.info('Creating the database tables...')
    # Note - enter the username and password for your database below.
    engine = create_engine("mysql+pymysql://<username>:<password>@127.0.0.1:3306/documents", 
                                      echo=True)
    SQLModel.metadata.create_all(engine)
    log.info('Database tables created.')

    id1, id2, id3 = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())

    doc1 = DOCUMENT(TEXT='This is the first document', PATH='data/doc1.txt', UUID=id1)
    doc2 = DOCUMENT(TEXT='This is the second document', PATH='data/doc2.txt', UUID=id2)
    doc3 = DOCUMENT(TEXT='This is the third document', PATH='data/doc3.txt', UUID=id3)

    print(doc1)

    log.info('Creating a session to the database...')
    with Session(engine) as session:
        session.add(doc1)
        session.add(doc2)
        session.add(doc3)
        session.commit()
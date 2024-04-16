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
import pandas as pd
from svlearn.common import *
import traceback
import logging as log


from sqlmodel import create_engine
import uuid
from sqlalchemy import create_engine
from svlearn.config import ConfigurationMixin


class WikipediaLoader:
    """
    Load wikipedia data from the parquet files. It assumes that
    you have downloaded the parquet files from the Kaggle website:
    https://www.kaggle.com/datasets/jjinho/wikipedia-20230701
    """

    def __init__(self, data_path: str):
        """
        Constructor for the WikipediaLoader class.
        :param data_path: the path to the data files.
        """
        if not directory_exists(data_path):
            log.error(
                f"Invalid data path: {data_path}."
                "It does not point to a valid, accessible directory."
            )
            raise ValueError(f"Invalid data path: {data_path}")

        self.data_path = Path(data_path)

    def open_connection(self) -> None:
        """
        This method opens a connection to the database.
        :return: None
        """
        config = ConfigurationMixin().load_config()
        username = config["database"]["username"]
        password = config["database"]["password"]
        server = config["database"]["server"]
        port = config["database"]["port"]
        connection_string = (
            f"mysql+pymysql://{username}:{password}@{server}:{port}/documents"
        )
        self.engine = create_engine(connection_string, echo=True)
        log.info(f"Opened connection to the database: {server}:{port}/documents")

    def load_parquet(self, file_name: str) -> pd.DataFrame:
        """
        This method loads the data from the given file.
        :param file_name: the name of the file to load.
        :return: a pandas dataframe with the data.
        """
        check_valid_file(file_name)
        log.info(f"Loading data from file: {file_name}")

        try:
            df = pd.read_parquet(file_name)
            # adding the path column
            df["PATH"] = df["id"].apply(lambda _: file_name)
            log.info(f"Loaded data from file: {file_name} with shape: {df.shape}")

            return df
        except Exception as e:
            log.error(
                f"Error while loading data from file: {file_name}. Error: {e}, Trace: {traceback.format_exc()}"
            )
            raise e

    def load_all_data(self) -> pd.DataFrame:
        """
        This method loads all the data from the data path.
        :return: a pandas dataframe with the data.
        """
        log.info(f"Loading all data from path: {self.data_path}")
        frames: [pd.DataFrame] = []
        try:
            for parquet_file in self.data_path.glob("*.parquet"):
                if (
                    "index" in parquet_file.name
                    or "other" in parquet_file.name
                    or "number" in parquet_file.name
                ):
                    continue
                print(f"Loading data from file: {parquet_file}")

                df = self.load_parquet(parquet_file)
                frames.append(df)
                log.info(f"Loaded data from the parquet file:{parquet_file}")
            complete_data = pd.concat(frames)
            log.info
            return complete_data
        except Exception as e:
            log.error(
                f"Error while loading data from path: {self.data_path}."
                f" Error: {e}, Trace: {traceback.format_exc()}"
            )
            raise e

    def persist_data(self, df: pd.DataFrame) -> None:
        """
        This method persists the data into the database.
        :return: None
        """
        log.info(f"Persisting data into database")
        try:
            # open the connection
            log.info(f"Opening connection to the database")
            df.to_sql("DOCUMENT", con=self.engine, if_exists="append", index=False)
            log.info(f"Persisted data into database")
        except Exception as e:
            log.error(
                f"""Error while persisting data into database. 
                Error: {e}, Trace: {traceback.format_exc()}"""
            )
            raise e

    def transform_data(self, df: pd.DataFrame) -> None:
        """
        This method transforms the data into the format required by the database.
        :param df: the pandas dataframe with the data.
        :return: a pandas dataframe with the transformed data.
        """
        log.info(f"Transforming data")
        try:
            # Add a UUID column; here the id col has been randomly picked for convenience.
            df["UUID"] = df.index.map(lambda _: str(uuid.uuid4()))
            df["TEXT"] = df["title"] + " " + df["text"]
            df["LANGUAGE"] = "en-us"
            df["DOCTYPE"] = "text"
            df["CHUNKED"] = False
            df["ES_INDEXED"] = False
            df.drop(["id", "title", "text", "categories"], axis=1, inplace=True)

        except Exception as e:
            log.error(
                f"Error while transforming data. Error: {e}, Trace: {traceback.format_exc()}"
            )
            raise e

    def etl(self) -> pd.DataFrame:
        """
        This method loads the data from the data path and persists it into the database.
        :return: a pandas dataframe with the data.
        """
        log.info(f"Loading data from path: {self.data_path}")
        try:
            df = self.load_all_data()
            self.transform_data(df)
            self.persist_data(df)
            return df
        except Exception as e:
            log.error(
                f"""Error while loading data from path: {self.data_path}.
                  Error: {e}, Trace: {traceback.format_exc()}"""
            )
            raise e


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loader = WikipediaLoader(data_path="/home/asif/Downloads/tmp/")
    total = loader.etl()
    print (total.describe())
    print (total.sample(10))

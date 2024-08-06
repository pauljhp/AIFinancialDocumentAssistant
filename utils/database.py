from collections import deque, OrderedDict
import types
import sqlalchemy
from typing import List, Literal, Optional, Union, Dict, Hashable, Any
import toml
import logging
import pandas as pd
import numpy as np
import datetime as dt
from sqlalchemy.engine import URL
import os


LOGGER = logging.getLogger("azure.core.pipeline.policies.http_logging_policy")
LOGGER.setLevel(logging.WARNING)

class Secrets(types.SimpleNamespace):
    """Singleton class containing login details"""
    def __init__(self, login_path: str="./.secrets/secrets.toml"):
        self.__SECRETS = os.environ
        self.__dict__.update({k: self.__elt(v) for k, v in self.__SECRETS.items()})
    
    def __elt(self, elt):
        """Recurse into elt to create leaf namespace objects"""
        if type(elt) is dict:
            return type(self)(elt)
        if type(elt) in (list, tuple):
            return [self.__elt(i) for i in elt]
        return elt

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Secrets, cls).__new__(cls)
            return cls.instance

SECRETS = Secrets()


class SQLDatabase:
    def __init__(
            self, 
            password: str=SECRETS.IFW_SQL_PW, 
            username: str=SECRETS.IFW_SQL_USERNAME, 
            driver: str=SECRETS.IFW_SQL_DRIVER,
            endpoint: str=SECRETS.IFW_SERVER, 
            database_name: str=SECRETS.IFW_DATABASE, 
            port: int=SECRETS.IFW_SQL_PORT
            ):
        __conn_str = 'DRIVER='+driver+';SERVER=tcp:'+endpoint+';PORT='+str(port)+';DATABASE='+database_name+';UID='+username+';PWD='+password
        __conn_url = URL.create("mssql+pyodbc", query={"odbc_connect": __conn_str})
        self.engine = sqlalchemy.create_engine(__conn_url)

    def query_to_pandas(self, query: str):
        with self.engine.connect().execution_options(autocommit=True) as conn:
            df = pd.read_sql(sqlalchemy.text(query), con=conn)
        return df

    @classmethod
    def to_pandas(cls, query: str, **kwargs):
        return cls(**kwargs).query_to_pandas(query)
    
    def get_table_schema(self, table_name: str) -> pd.DataFrame:
        with self.engine.connect() as conn:
            schema = pd.read_sql(
                sqlalchemy.text(f"select * from INFORMATION_SCHEMA.COLUMNS where TABLE_NAME='{table_name}'"),
                con=conn
            )
        return schema
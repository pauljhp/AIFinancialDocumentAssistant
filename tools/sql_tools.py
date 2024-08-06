from llama_index.core import SQLDatabase
from llama_index.llms.azure_openai import AzureOpenAI

from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.experimental.query_engine import PandasQueryEngine
import json
import utils


default_table = "ai_assistant_esg_board" # FIXME - wrap table names into secrets

llm = AzureOpenAI(deployment_name="gpt-35-16k", 
        model="gpt-35-turbo-16k", 
        temperature=0,
        context_window=16384,
        api_version="2023-07-01-preview")

sql_database = SQLDatabase(
    utils.SQLDatabase().engine, 
    include_tables=[default_table] # FIXME - wrap table names into secrets
    )

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=[default_table], llm=llm,
    verbose=True
)

def get_schema(table_name: str=default_table):
    schema = utils.SQLDatabase().get_table_schema(table_name)
    return schema

def answer_query(query_str: str=f"What is the average tenure of TSMC's (ISIN: TW0002330008) board?"):
    schema = get_schema()[["TABLE_NAME", "COLUMN_NAME"]]
    schema_engine = PandasQueryEngine(df=schema, verbose=True, synthesize_response=True, llm=llm)
    schema_query = (f"You are given a dataframe, containing the table names (`TABLE_NAME`), "
            f"and columns names (`COLUMN_NAME`). You are supposed to use {default_table}. "
            "Based on the pandas dataschema, find out the column that could help you answer "
            f"the user query: {query_str}. "
            "Think step by step about which fields are needed, and how to query for the company mentioned. "
            "Beware that the column name might not be exactly the same as what you expect, "
            "so try to use the str.contains method and be careful about case. "
            "Use structured identifiers such as ISIN or SEDOL, if given. Try not to use company name as it might be fuzzy. ")
    rewrite = schema_engine.query(schema_query)
    columns_str = " ".join(schema.COLUMN_NAME)
    print(rewrite)
    rewritten_question = (f"You are asked this question {query_str}. "
                f"Your table shema has the following columns: {columns_str}. "
                f"Your colleague gave you this comment: {str(rewrite.response)}. "
                "Answer the question using the information above. "
                "Hint: If you find multiple entries, sort by `date` and return the latest. "
                "Hint: Try and use the structured identifiers, such as ISIN, if provided. "
                )
    response = query_engine.query(rewritten_question)
    print(response)
    return response.response
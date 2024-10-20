"""constructor of retriever objects"""

from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.selectors import PydanticMultiSelector
# from llama_index.core.retrievers import RouterRetriever
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core import PromptTemplate
from llama_index.core import SummaryIndex
from qdrant_client.http.models import (
    Filter,
    # FieldCondition, 
    # MatchValue
)
from tasks import get_pillar_datafields
from settings import (
    li_llm, 
    li_llm_4o
)
# from tasks import task_descriptions 
from data_models import CompanyInfo, ESGSection, ESGPillar
from typing import List


def get_base_retriever(
          index, 
          filters: List[Filter], 
          similarity_top_k: int=10
          ):
    return index.as_retriever(
         similarity_top_k=similarity_top_k,
         vector_store_kwargs={"qdrant_filters": filters}
         )
    

def get_recursive_retriever(base_retriever):
    return RecursiveRetriever(
        root_id="vector", 
        retriever_dict=dict(vector=base_retriever), 
        verbose=True
        )

def generate_queries(
        llm, 
        query_str: str, 
        num_queries: int = 15
        ):
        query_gen_prompt_str = (
                "You are an intelligent analyst looking at companies' ESG performances. "
                "You are given a larger question which needs to be broken down into steps. "
                "Rewrite the larger question into smaller sizes as you see fit, with "
                "around {num_queries} sub-queries. " 
                "Note that some queries may contain acronyms, so try to be detailed in the "
                "new queries you write. "
                "ONLY GENERATE QUERIES AND DONT ANSWER. "
                "Generate more queries for following input query:\n"
                "Query: {query_str}\n"
                "Queries:\n"
            )
        query_gen_prompt = PromptTemplate(query_gen_prompt_str)
        fmt_prompt = query_gen_prompt.format(
            num_queries=num_queries, query_str=query_str
        )
        response = llm.complete(fmt_prompt)
        queries = response.text.split("\n")
        for i in queries:
            if i == '':
                queries.remove(i)
        return queries

def rewrite_template(
          company_info: CompanyInfo,
          section: ESGSection,
          subsection: ESGPillar,
          llm=li_llm_4o,
          num_queries: int=10
    ):
    description = get_pillar_datafields(
         company=company_info,
         section=section, 
         subsection=subsection,
         )
    queries = generate_queries(
         llm,
         query_str=description,
         num_queries=num_queries
    )
    return queries
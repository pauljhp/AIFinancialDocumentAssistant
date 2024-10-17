from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.core import (
    VectorStoreIndex, StorageContext, ServiceContext,
    QueryBundle
    )
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.schema import NodeWithScore
from qdrant_client import QdrantClient, models, AsyncQdrantClient
import os

from data_models import CompanyInfo, ESGPillar, ESGSection
from settings import (
    embed_model, 
    llm, li_llm,
    llm_4o, li_llm_4o
)
from .retrievers import (
    rewrite_template,
    get_base_retriever,
    get_recursive_retriever
)
from typing import List, Dict, Tuple


qdrant_endpoint = os.getenv("QDRANT_ENDPOINT")
qdrantclient = QdrantClient(
    qdrant_endpoint, 
    port=os.getenv("QDRANT_PORT"), 
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=150
    )
qdrantaclient = AsyncQdrantClient(
    qdrant_endpoint, 
    port=os.getenv("QDRANT_PORT"), 
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=150
    )


def get_qdrantstore(collection_name: str="esg_reports"):
    # if use_async:
    #     qdrant_store = QdrantVectorStore(
    #         aclient=qdrantaclient,
    #         parallel=2,
    #         collection_name=collection_name,
    #         enable_hybrid=True
    
    #     )
    qdrant_store = QdrantVectorStore(
            aclient=qdrantaclient,
            client=qdrantclient,
            parallel=2,
            collection_name=collection_name,
            enable_hybrid=True
        )
    return qdrant_store

def get_index(collection_name: str):
    """returns an existing collection as index"""
    # service_context = ServiceContext.from_defaults(
    #     llm_predictor=llm,
    # )
    index = VectorStoreIndex.from_vector_store(
        vector_store=get_qdrantstore(collection_name),
        embed_model=embed_model,
        # collection=collection
    )
    return index

def get_query_engine(collection: str):
    index = get_index(collection)
    return index.as_query_engine(llm=li_llm)

def get_query(
        query_str: str, 
        embed_model=embed_model, 
        # top_k: int=10,
        # mode: VectorStoreQueryMode=VectorStoreQueryMode.DEFAULT
    ) -> QueryBundle:
    query_embedding = embed_model.get_query_embedding(query_str)
    query = QueryBundle(
        query_str=query_str, 
        embedding=query_embedding
    )
    return query

async def arun_queries(
        queries: List[QueryBundle], 
        retrievers: List[AsyncQdrantClient]
        ) -> List[Dict[str, str]]:#List[Dict[str, QueryBundle | Dict[str, str]]]:
    """Run queries against retrievers."""
    task_results = []
    for query in queries:
        for retriever in retrievers:
            res = await retriever.aretrieve(query)
            task_results += res

    # results = [dict(query=query, result=result) for query, result in zip(queries, task_results)]
    return sorted(task_results, key=lambda x: x.score if x.score else 0.0, reverse=True)

async def arun_esg_pillar(
        company_info: CompanyInfo,
        section: ESGSection,
        subsection: ESGPillar,
        collections: List[str]=["esg_reports", "annual_reports", "annual_report2"],  
        llm=li_llm_4o
    ):
    retrievers = [
        get_base_retriever(
            get_index(collection), 
            filters=company_info.as_qdrant_filter()
            )
        for collection in collections]
    retrievers = [get_recursive_retriever(retriever) for retriever in retrievers]
    rewritten_queries = rewrite_template(
        company_info=company_info,
        section=section,
        subsection=subsection,
        llm=llm
    )
    res = await arun_queries(queries=rewritten_queries, retrievers=retrievers)
    return res

def fuse_results(
        results: List[Dict[str, str]],#Dict[Tuple[QueryBundle, int], Dict[str, str]], 
        similarity_top_k: int = 10
        ):
    k = 50.0  # `k` is a parameter used to control the impact of outlier rankings.
    fused_scores = {}
    text_to_node = {}

    for rank, node_with_score in enumerate(results):
        text = node_with_score.node.get_content()
        text_to_node[text] = node_with_score
        if text not in fused_scores:
            fused_scores[text] = 0.0
        fused_scores[text] += 1.0 / (rank + k)

    reranked_results = dict(
        sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    )

    # adjust node scores
    reranked_nodes = []
    for text, score in reranked_results.items():
        reranked_nodes.append(text_to_node[text])
        reranked_nodes[-1].score = score

    return reranked_nodes[:similarity_top_k]
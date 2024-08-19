from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, ServiceContext
from qdrant_client import QdrantClient, models
from settings import embed_model, llm, li_llm
import os

qdrant_endpoint = os.getenv("QDRANT_ENDPOINT")
qdrantclient = QdrantClient(
    qdrant_endpoint, 
    port=os.getenv("QDRANT_PORT"), 
    api_key=os.getenv("QDRANT_API_KEY")
    )


def get_qdrantstore(collection_name: str="dev_esg_collection"):
    qdrant_store = QdrantVectorStore(
        client=qdrantclient,
        collection_name=collection_name
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
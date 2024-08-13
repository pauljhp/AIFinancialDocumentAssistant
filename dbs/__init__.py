from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import VectorStoreIndex, StorageContext, ServiceContext
from qdrant_client import QdrantClient, models
from settings import embed_model, llm
import os

qdrant_endpoint = os.getenv("QDRANT_ENDPOINT")
qdrantclient = QdrantClient(
    qdrant_endpoint, 
    port=os.getenv("QDRANT_PORT"), 
    api_key=os.getenv("QDRANT_API_KEY")
    )

qdrant_store = QdrantVectorStore(
    client=qdrantclient,
    collection_name="dev_esg_collection"
)
storage_context = StorageContext.from_defaults(
    vector_store=qdrant_store
    )

def get_index(collection: str):
    """returns an existing collection as index"""
    # service_context = ServiceContext.from_defaults(
    #     llm_predictor=llm,
    # )
    index = VectorStoreIndex.from_vector_store(
        vector_store=qdrant_store,
        embed_model=embed_model,
        collection=collection
    )
    return index

def get_query_engine(collection: str):
    index = get_index(collection)
    return index.as_query_engine()
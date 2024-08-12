from llama_index.core.indices.tree import TreeIndex
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.schema import MetadataMode
from fastembed import TextEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client import QdrantClient, models
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core import Settings
from typing import Dict, List
import os

Settings.embed_model = FastEmbedEmbedding()
qdrant_endpoint = os.getenv("QDRANT_ENDPOINT")
qdrantclient = QdrantClient(qdrant_endpoint, port=6333, api_key=os.getenv("QDRANT_API_KEY"))


def create_documents_from_results(results: Dict[str, Dict[str, str]]):
    documents = []
    for elem in results:
        document = Document(
            text=elem["text"],
            metadata_template=elem["metadata_template"],
            doc_id=elem["id_"],
            metadata=elem["metadata"]
            )
        documents.append(document)
    return documents
    

def create_index(collection_name: str, documents: List[Document]):
    qdrant_store = QdrantVectorStore(
        client=qdrantclient,
        collection_name=collection_name
    )
    storage_context = StorageContext.from_defaults(vector_store=qdrant_store)
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context
    )
    return index
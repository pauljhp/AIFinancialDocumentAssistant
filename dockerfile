FROM ubuntu:20.04

RUN conda -n ai_env \   
    pip install llama-index \
                llama-index-core \
                llama-index-retrievers-bm25 \
                llama-index-llms-azure-openai \
                llama-index-embeddings-azure-openai \
                llama-index-postprocessor-cohere-rerank \
                llama-index-vector-stores-qdrant \
                pydantic \
                fastapi
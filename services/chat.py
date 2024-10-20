"""Interactive chat with the AI about completed results"""
from data_models import (
    CompanyInfo,
    ESGPillar,
    ESGSection
)
from .precomputed_results import read_from_sql
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.legacy.prompts.base import PromptTemplate
from llama_index.legacy.core.llms.types import ChatMessage, MessageRole
from llama_index.legacy.chat_engine import ContextChatEngine
from llama_index.legacy.chat_engine.condense_question import CondenseQuestionChatEngine
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.storage.chat_store import SimpleChatStore
from typing import List
from dbs import get_base_retriever, get_recursive_retriever, get_index
from settings import li_llm_4o, get_service_context


chat_store = SimpleChatStore()
# chat_store.persist()
chat_prompt = PromptTemplate(
    """\
You are a helpful assistant experienced in answer ESG related questions.
You are provided with information related to the company to be queries about.

<Chat History>
{chat_history}

<User Question>
{question}

"""
)

def get_chat_engine(
    session_id: str,
    company_info: CompanyInfo,
    collections: List[str]=["esg_reports", "annual_reports"],  
    similarity_top_k: int=30,
    llm=li_llm_4o,
    ):
    memory = ChatMemoryBuffer.from_defaults(
        llm=li_llm_4o, 
        token_limit=100000,
        chat_store_key=session_id,
        chat_store=chat_store
        )
    retrievers = [
        get_base_retriever(
            get_index(collection), 
            filters=company_info.as_qdrant_filter(),
            similarity_top_k=similarity_top_k
            )
        for collection in collections]
    retrievers = [get_recursive_retriever(retriever) for retriever in retrievers]
    retriever = QueryFusionRetriever(
        retrievers,
        llm=llm,
        mode="relative_score",
        similarity_top_k=similarity_top_k,
        use_async=True,
        num_queries=1,
        verbose=True # TODO - change to False for prod
    )
    chat_history = [
        ChatMessage(
            role=MessageRole.SYSTEM,
            content="Your your is to assist user with questions",
        )
    ]

    # Create the chat engine using the custom prompt and query engine
    chat_engine = ContextChatEngine.from_defaults(
        retriever=retriever,
        chat_history=chat_history,
        memory=memory,
        verbose=True,
        service_context=get_service_context(),
        llm=li_llm_4o
    )
    return chat_engine


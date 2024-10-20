from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core.indices.prompt_helper import PromptHelper
from llama_index.core.indices.service_context import ServiceContext
from llama_index.core.node_parser import SentenceSplitter

from langchain_openai.chat_models import AzureChatOpenAI
from langfuse.callback import CallbackHandler
from langfuse.decorators import langfuse_context, observe
import os


langfuse_callback_handler = LlamaIndexCallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

langfuse_handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

callback_manager = CallbackManager([langfuse_callback_handler])

# langfuse_context.update_current_trace(
#     public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#     secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#     host=os.getenv("LANGFUSE_HOST")
# )

li_llm = AzureOpenAI(
    engine=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    model="gpt-35-turbo-16k",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    callback_manager=callback_manager,
    temperature=0.
)

li_llm_4o = AzureOpenAI(
    engine=os.getenv("AZURE_GPT4o_DEPLOYMENT_NAME"),
    model="gpt-4o-mini",
    api_key=os.getenv("AZURE_OPENAI_GPT4o_KEY"),
    api_version=os.getenv("AZURE_GPT4o_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_GPT4o_ENDPOINT"),
    callback_manager=callback_manager,
    temperature=0.
)

llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    model_name="gpt-35-turbo-16k",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    callbacks=[langfuse_handler],
    temperature=0.
)

llm_4o = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_GPT4o_DEPLOYMENT_NAME"),
    model_name="gpt-4o-mini",
    api_key=os.getenv("AZURE_OPENAI_GPT4o_KEY"),
    api_version=os.getenv("AZURE_GPT4o_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_GPT4o_ENDPOINT"),
    callbacks=[langfuse_handler],
    temperature=0.
)

function_llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT"),
    model_name="gpt-4", # GPT-4 has better function calling capabilities
    api_key=os.getenv("AZURE_OPENAI_GPT4_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_GPT4_ENDPOINT"),
    callbacks=[langfuse_handler],
    temperature=0.
    # strict=True
)

embed_model = FastEmbedEmbedding(
    model_name="BAAI/bge-small-en-v1.5"
    )

def get_prompt_helper(context_window: int=128000) -> PromptHelper:
    num_output = context_window // 4
    chunk_overlap_ratio = 0.1
    chunk_size_limit = min(1600, context_window // 10)
    prompt_helper = PromptHelper(
        context_window=context_window,
        num_output=num_output,
        chunk_overlap_ratio=chunk_overlap_ratio,
        chunk_size_limit=chunk_size_limit
    )
    return prompt_helper

def get_service_context(context_window: int=128000):
    prompt_helper = get_prompt_helper(context_window=context_window)
    service_context = ServiceContext.from_defaults(
        llm=li_llm_4o,
        prompt_helper=prompt_helper,
        embed_model=embed_model
    )
    return service_context

def set_global_configs(**kwargs):
    from llama_index.core import Settings
    Settings.callback_manager = callback_manager 
    Settings.llm = li_llm_4o
    Settings.embed_model = embed_model
    Settings.context_window = kwargs.get("context_window", 128000)
    Settings.node_parser = SentenceSplitter(
        chunk_size=kwargs.get("chunk_size", 1024),
        chunk_overlap=kwargs.get("chunk_overlap", 100)
        )

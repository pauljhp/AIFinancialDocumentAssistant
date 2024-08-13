from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.llms.azure_openai import AzureOpenAI
from langchain_openai.chat_models import AzureChatOpenAI
import os

 
langfuse_callback_handler = LlamaIndexCallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

li_llm = AzureOpenAI(
    engine=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    model="gpt-35-turbo-16k",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    model_name="gpt-35-turbo-16k",
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

function_llm = AzureChatOpenAI(
    deployment_name=os.getenv("AZURE_OPENAI_GPT4_DEPLOYMENT"),
    model_name="gpt-4",
    api_key=os.getenv("AZURE_OPENAI_GPT4_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_GPT4_ENDPOINT"),
    # strict=True
)

embed_model = FastEmbedEmbedding()

def set_global_configs():
    from llama_index.core import Settings
    Settings.callback_manager = CallbackManager([langfuse_callback_handler])
    Settings.llm = li_llm
    Settings.embed_model = embed_model
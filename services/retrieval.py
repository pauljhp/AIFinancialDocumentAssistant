#!sudo apt-get install poppler-utils -y
import os
import time
import os
import pandas as pd
import fitz
import nltk
import requests
import PyPDF2
import numpy as np
from io import BytesIO
from PIL import Image
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client import AsyncQdrantClient
from llama_index.core import Settings
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core import (
 VectorStoreIndex,
 ServiceContext,
 SimpleDirectoryReader,
)
from llama_index.core.vector_stores import VectorStoreQuery
from llama_index.core import QueryBundle
from llama_index.core.schema import NodeWithScore
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
    BaseExtractor,
)
from llama_index.core import QueryBundle
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import NodeWithScore
import asyncio
from typing import Any, List
from llama_index.core.retrievers import BaseRetriever
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.core.node_parser.text import SentenceSplitter
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.fastembed import FastEmbedEmbedding
azure_endpoint: str = "https://impax-openai-dev.openai.azure.com/"
os.environ["AZURE_OPENAI_ENDPOINT"] = azure_endpoint
azure_openai_api_key: str = "b2b66f4cb2974b58bbe05d07482467d7"
os.environ["AZURE_OPENAI_API_KEY"] = azure_openai_api_key
azure_openai_api_version: str = "2024-02-15-preview"
azure_deployment: str = "text-embedding-ada-002"
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING']='1'
results_dict = {}
os.environ['OPENAI_API_KEY']=azure_openai_api_key
os.environ['OPENAI_API_TYPE']='azure'
from llama_index.core.vector_stores import MetadataFilter,MetadataFilters,FilterOperator
from llama_index.core.retrievers import RecursiveRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core import get_response_synthesizer
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from typing import List
from llama_index.core.schema import NodeWithScore
import warnings
warnings.filterwarnings('ignore')
Settings.llm=llm
Settings.embed_model=embed_model
Settings.chunk_size_limit=1024
Settings.context_window=4096

temp=pd.read_csv('esg_templates.csv')
esg_samples=pd.read_csv('esg_samples.csv')
#print(esg_samples.loc[esg_samples['company_name'] == 'TRIP.COM'])
gics_sector =esg_samples.loc[esg_samples['company_name'] == 'TRIP.COM', 'GICS_sector'].iloc[0]
print(gics_sector)
temp = temp[temp['sector'] == gics_sector]

import nest_asyncio
nest_asyncio.apply()

company_name='TRIP.COM'
company_names=[company_name]#,'AMAZON.COM INC', 'MASTERCARD INC', 'ASML HOLDING', 'HONG KONG EXCHANGES & CLEAR']

llm = AzureOpenAI(deployment_name="ipx_openai_llm", 
        model="gpt-3.5-turbo-16k", 

        api_version="2024-02-15-preview", openai_api_key=azure_openai_api_key,temperature=0)
#model="gpt-3.5-turbo-16k"
client = QdrantClient("http://52.148.166.222:6333", api_key="impaxam24", port=6333)

embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-en-v1.5")

Settings.embed_model = embed_model
os.environ["CUDA_VISIBLE_DEVICES"]=""

names=['Toronto-Dominion Bank','Yara International','Westpac Banking Corp' 'Banking Corp','Loreal','Citigroup', 'Zoetis Inc', 'Nvidia Corp', 'Halma PLC', 'Severn Trent plc', 'Schneider Electric']

cohere_rerank = CohereRerank(api_key="RYc3b7jarv8vGuqOprZPn3zIMlOiP5P6J0nuWTBH", top_n=10)
## I have separate classes for each ESG and Annual in case we want to add specifics to either later on
from qdrant_client.http import models
qfilter=models.Filter(
        must=[
            models.FieldCondition(
                key="report_year",
                match=models.MatchValue(
                    value=2023, 
                )
            ),
        ]
    )

    
#initialize storage variables for both esg and annual report indexes
##esg rep index
vector_store = QdrantVectorStore(client=client, collection_name="esg_reports", enable_hybrid=True)

storage_context = StorageContext.from_defaults(
    vector_store=vector_store
)


esg_index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store)
##annual report index
vector_store_2 = QdrantVectorStore(client=client, collection_name="annual_reports", enable_hybrid=True)

storage_context_2 = StorageContext.from_defaults(
    vector_store=vector_store_2
)

annual_report_index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store_2)

class VectorDBRetriever_esg(BaseRetriever):
    def __init__(
    self,
    vector_store: QdrantVectorStore,
    embed_model: Any,
    query_mode: str = "default",
    
    similarity_top_k: int = 5,
    ) -> None:
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:

        index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store)


        """Retrieve."""
        query_embedding = embed_model.get_query_embedding(
        query_bundle.query_str
        )
        vector_store_query = VectorStoreQuery(
        query_embedding=query_embedding,
        similarity_top_k=self._similarity_top_k,
        mode=self._query_mode,
        )
        query_result = vector_store.query(vector_store_query)#,qdrant_filters=qfilter)
        
        nodes_with_scores = []
        processor = SimilarityPostprocessor(similarity_cutoff=0.7)
        
        for index, node in enumerate(query_result.nodes):
            


            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
                #post query filtering, currently commented out
                
                #if node.metadata['company name'] == company_name:
                
                #    nodes_with_scores.append(NodeWithScore(node=node, score=score))
        #print(nodes_with_scores)

        return nodes_with_scores

class VectorDBRetriever_annual(BaseRetriever):
    def __init__(
    self,
    vector_store: QdrantVectorStore,
    embed_model: Any,
    query_mode: str = "default",
    
    similarity_top_k: int = 5,
    ) -> None:
        self._vector_store = vector_store
        self._embed_model = embed_model
        self._query_mode = query_mode
        self._similarity_top_k = similarity_top_k
        super().__init__()
    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        
       #############change idx according to route#####################
        index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store_2)

        """Retrieve."""
        query_embedding = embed_model.get_query_embedding(
        query_bundle.query_str
        )
        vector_store_query = VectorStoreQuery(
        query_embedding=query_embedding,
        similarity_top_k=self._similarity_top_k,
        mode=self._query_mode,
        )
        #use qdrant_filters kwarg if filtering while querying
        query_result = vector_store_2.query(vector_store_query)#,qdrant_filters=qfilter)
        
        nodes_with_scores = []
        processor = SimilarityPostprocessor(similarity_cutoff=0.7)
        
        for index, node in enumerate(query_result.nodes):
            


            score: Optional[float] = None
            if query_result.similarities is not None:
                score = query_result.similarities[index]
                #post query filtering, currently commented out
                
                #if node.metadata['company name'] == company_name:
                
                #    nodes_with_scores.append(NodeWithScore(node=node, score=score))
        #print(nodes_with_scores)

        return nodes_with_scores


retriever_esg = VectorDBRetriever_esg(
vector_store, embed_model, query_mode="default"
)

retriever_annual = VectorDBRetriever_annual(
vector_store_2, embed_model, query_mode="default")


vector_retriever_esg = esg_index.as_retriever(vector_store_kwargs={"qdrant_filters": qfilter})
vector_retriever_annual = annual_report_index.as_retriever(vector_store_kwargs={"qdrant_filters": qfilter})

recursive_retriever_esg = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_esg}  ,  verbose=True,
)
response_synthesizer = get_response_synthesizer(response_mode="compact", llm=llm) 

recursive_retriever_query_engine_esg = RetrieverQueryEngine.from_args(
    recursive_retriever_esg,llm=llm,response_synthesizer=response_synthesizer,node_postprocessors=[cohere_rerank]
)
retriever_query_engine_esg = RetrieverQueryEngine.from_args(
   vector_retriever_esg,llm=llm,response_synthesizer=response_synthesizer,node_postprocessors=[cohere_rerank])

##########now for annual reps:
recursive_retriever_annual = RecursiveRetriever(
    "vector",
    retriever_dict={"vector": vector_retriever_annual}  ,  verbose=True,
)
response_synthesizer_annual = get_response_synthesizer(response_mode="compact", llm=llm) 

recursive_retriever_query_engine_annual = RetrieverQueryEngine.from_args(
    recursive_retriever_annual,llm=llm,response_synthesizer=response_synthesizer_annual,node_postprocessors=[cohere_rerank]
)
retriever_query_engine_annual = RetrieverQueryEngine.from_args(
   vector_retriever_annual,llm=llm,response_synthesizer=response_synthesizer_annual,node_postprocessors=[cohere_rerank]
)



async def run_queries(queries, retrievers):
    """Run queries against retrievers."""
    tasks = []
    for query in queries:
        for i, retriever in enumerate(retrievers):
            tasks.append(retriever.aretrieve(query))

    task_results = await tqdm.gather(*tasks)

    results_dict = {}
    for i, (query, query_result) in enumerate(zip(queries, task_results)):
        results_dict[(query, i)] = query_result

    return results_dict



def fuse_results(results_dict, similarity_top_k: int = 10):

    k = 50.0  # `k` is a parameter used to control the impact of outlier rankings.
    fused_scores = {}
    text_to_node = {}

    for nodes_with_scores in results_dict.values():
        for rank, node_with_score in enumerate(
            sorted(
                nodes_with_scores, key=lambda x: x.score or 0.0, reverse=True
            )
        ):
            text = node_with_score.node.get_content()
            text_to_node[text] = node_with_score
            if text not in fused_scores:
                fused_scores[text] = 0.0
            fused_scores[text] += 1.0 / (rank + k)

    reranked_results = dict(
        sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    )

    # adjust node scores
    reranked_nodes: List[NodeWithScore] = []
    for text, score in reranked_results.items():
        reranked_nodes.append(text_to_node[text])
        reranked_nodes[-1].score = score

    return reranked_nodes[:similarity_top_k]

final_results = fuse_results(results_dict)


class FusionRetriever(BaseRetriever):

    def __init__(
        self,
        llm,
        retrievers: List[BaseRetriever],
        similarity_top_k: int = 10,
    ) -> None:
       
        self._retrievers = retrievers
        self._similarity_top_k = similarity_top_k
        self._llm = llm
        super().__init__()

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        
        queries = generate_queries(
            self._llm, query_bundle.query_str, num_queries=5
        )
        results = asyncio.run(run_queries(queries, self._retrievers))
        final_results = fuse_results(
            results, similarity_top_k=self._similarity_top_k
        )

        return final_results

def get_results(temp, company_names,retriever_esg,recursive_retriever_esg,retriever_annual, recursive_retriever_annual):
    for company_name in company_names:
        
        for index, row in temp.iterrows():
            indicator=row['indicators']
            pillar=row['pillar']
            print(pillar)
            print(indicator)
            print(company_name)

            prompt_pillars="""You are a critical ESG information retriever analysing the company {}.  You are given a list of indicators you have to retrieve with heavy detail. for each indicator, refer to its  reports provided to you, and output a descriptive answer about it with statistics, details from tables, supporting information, etc such that each mentioned bullet point is several sentences to a paragraph long. Return anything relevant TO the indicator: you should be as detailed as possible. RETRIEVE AS MUCH INFO AS YOU CAN - IF IT IS MENTIONED IN THE REPORT, RETURN ALL OF IT. LOOK FOR EXACT NUMBERS AND PERCENTAGES FOR EACH.  for each fact you mention, give numbers/statistics/examples to back it up.
            The indicators are: 
            {}

            
            I DONT WANT ANY HEADINGS WITH THE INDICATORS.
            SAMPLE OUTPUT FOR EACH INDICATOR:
            Company X mentions the percentage of water saved in gallons/ton. in 2023 thar percentage was 23%, about 5 percentage points up from 2021. Company X aims to improve this number in the coming years. Company X aslo has various programs such as the waterworks program and W initiative to achieve this.
            ANOTHER SAMPLE OUTPUT:
            COMPANY X has a board of diirectors from diverse backgrounds. for example Mr.Y has a background in X and mr. Z has a background in XYZ.

            SAMPLE OUTPUT FOR  INDICATOR where no info was found:
            No response

            MOST IMPORTANTLY: ABSOLUTELY DO NOT BE VAGUE. RETURN SPECIFICS AND NOT GENERAL THINGS MENTIONED IN REPORTS. Dont simply write: the company mentions or the company doesnt mention. I WANT DETAIL. AND RETURN ANYTHING RELEVANT TO INDICATORS THAT ISNT LISTED.
            """.format(company_name,indicator)
            
            print(prompt_pillars)

            prompt=prompt_pillars
            #for index,prompt in enumerate(prompts):
            #prompt_type=prompt_types[index]
            
            query_gen_prompt_str = (
                "You are a helpful assistant that generates multiple search queries based on a "
                "single input query. Generate {num_queries} search queries, one on each line. , ONLY GENERATE QUERIES AND DONT ANSWER TO QUERY"
                "related to the following input query:\n"
                "Query: {query}\n"
                "Queries:\n"
            )
            query_gen_prompt = PromptTemplate(query_gen_prompt_str)


            ##this gets n subquestions from the query. results in a more thorough analysis than one broad query
            query_str=prompt
            def generate_queries(llm, query_str: str, num_queries: int =  35):
                fmt_prompt = query_gen_prompt.format(
                    num_queries=num_queries - 1, query=query_str
                )
                response = llm.complete(fmt_prompt)
                queries = response.text.split("\n")
                for i in queries:
                    if i == '':
                        queries.remove(i)
                return queries

            queries = generate_queries(llm, query_str, num_queries=35)
            print(queries)

            nest_asyncio.apply()
            ##gets the nodes that pertain to the previous queries

            async def run_queries(queries, retrievers):
                """Run queries against retrievers."""
                tasks = []
                for query in queries:
                
                    for i, retriever in enumerate(retrievers):
                        tasks.append(retriever.aretrieve(query))

                task_results = await tqdm.gather(*tasks)

                results_dict = {}
                for i, (query, query_result) in enumerate(zip(queries, task_results)):
                    results_dict[(query, i)] = query_result

                return results_dict

            #we have 4 retrievers: a recursive and non-recursive one, each for eag and annual 
            results_dict = asyncio.run(run_queries(queries, [retriever_esg,recursive_retriever_esg,retriever_annual, recursive_retriever_annual]))

            final_results = fuse_results(results_dict)

            ##query engine just for fusion retriever
            response_synthesizer = get_response_synthesizer(response_mode="compact", llm=llm)

            from llama_index.core.query_engine import RetrieverQueryEngine
            fusion_retriever = FusionRetriever(
                llm, [retriever_esg, recursive_retriever_esg, retriever_annual, recursive_retriever_annual], similarity_top_k=15
            )

            
            query_engine = RetrieverQueryEngine.from_args(fusion_retriever,llm=llm, response_synthesizer=response_synthesizer)

            fusion_response = query_engine.query(query_str)

            print(str(fusion_response))
            file = open("esg_answers.txt", "a")

            meta=''
                    
            urls=[]
            pg=[]
            composite_figi=[]
            report_type=[]
            access_datetime=[]
            #company_name=[]
            data=''
            
            for key, value in fusion_response.metadata.items():
                page_number = value.get('page number')
                url = value.get('url')
                comp_name = value.get('company name')
                comp_figi = value.get('composite_figi')
                rep_type = value.get('report_type')
                urls.append(url)
                pg.append(page_number)
                print(fusion_response.metadata)
            
                retrieved_pdf_name=str(comp_name) +"_"+ str(comp_figi) + "_"+str(rep_type)+ "_"+str(page_number)+ "_.png"
            
            #data=str('\n'+str(company_name) + ' \n ' + str(prompt_type) + ' \n '+ str(fusion_response) + '\n' +'Metadata:'+ ' \n'+ 'urls\n' + str(urls)+'\nmeta:\n'+str(fusion_response.metadata) )
            data=str('\n'+str(company_name) + ' \n ' + str(pillar) + ' \n '+ str(fusion_response) + '\n' )

            

            def get_pdf_page_as_image(pdf_url, page_number):
                

                print(page_number)
                page_number=int(page_number)
                response = requests.get(pdf_url)
                pdf_data = response.content

                pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
                page = pdf_document[page_number]
                pix = page.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                return img


            try:
                image = get_pdf_page_as_image(url, page_number)
                image.save('retrieved_pdfs/'+retrieved_pdf_name)  
            except:
                pass
            

            print(data)

            file.write(data)

            # Close the file
            file.close()
        

get_results(temp, company_names,retriever_esg,recursive_retriever_esg,retriever_annual, recursive_retriever_annual)


            










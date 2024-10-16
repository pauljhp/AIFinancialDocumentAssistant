from crewai_tools import tool, LlamaIndexTool
from crewai_tools.tools.base_tool import BaseTool
from pydantic.v1 import BaseModel, Field
from pydantic import model_validator
from settings import li_llm, llm
from dbs import get_index, get_query_engine, arun_queries, get_query
from data_models import CompanyInfo
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
    FilterCondition
)
from llama_index.core.tools import (
    QueryEngineTool,
    ToolMetadata,
)
from typing import List, Dict, Annotated, Type, Any, Callable, Optional
from viztracer import log_sparse
from crewai.utilities import Printer
import asyncio


class QueryEngineSchema(BaseModel):
    pass

class RetrievalToolSchema(QueryEngineSchema, BaseModel):
    """Input for the `Vector DB Retrieval Tool`"""
    question: str = Field(
        ...,
        description="The question you are tring to ask to the database. "
        )


class QueryEngineResponse(BaseModel):
    response: str = Field(..., description="The immediate response")
    sources: str = Field(
        ...,
        description="The source of the information, converted to string"
        )


def get_query_engine_tool(
        collection_name: str,
        company_info: CompanyInfo=CompanyInfo(),
        filter_keys: List[str] = ["sedol", "isin", "figi"]
):
    filters = [
        MetadataFilter(key=key, value=value)
        for key, value
        in company_info.model_dump().items()
        if (value is not None and key in filter_keys)
    ]
    index = get_index(collection_name=collection_name)
    if filters:
        metadata_filters = MetadataFilters(
            filters=filters,
            condition=FilterCondition.AND
        )
        engine = index.as_query_engine(
            llm=li_llm,
            filters=metadata_filters
        )
    else:
        engine = index.as_query_engine(llm=li_llm)
    # query_tool = LlamaIndexTool.from_query_engine(
    #     query_engine=engine,
    #     name="Vector DB Retrieval Tool",
    #     description=("Tool for retrieving information fromm the vector "
    #                  "store about a particular company. You inputs MUST be a string."),
    #     args_schema=QueryEngineSchema
    # )
    query_tool = QueryEngineTool(
        query_engine=engine,
        metadata=ToolMetadata(
            name="Vector DB Retrieval Tool",
            description=("Tool for retrieving information fromm the vector "
                         "store about a particular company. You inputs MUST be a string."),
            fn_schema=RetrievalToolSchema,
            # return_direct=True
        )
    )
    print(query_tool.metadata)
    query_tool = LlamaIndexTool.from_tool(query_tool)
    # query_tool = query_tool.to_langchain_tool()
    return query_tool


class RetrievalTools(BaseTool):
    """Subclassing implementation of the retrieval tool"""
    name: str = "Vector DB Retrieval Tool"
    description: str = """Tool for retrieving information fromm the vector "
    "store about a particular company. You MUST pass in your question "
    "with the  `question` key, like this: `{"question": "sample question"}`"""
    args_schema: Type[BaseModel] = RetrievalToolSchema
    filter_keys: List[str] = ["sedol", "isin", "figi"]
    company_info: CompanyInfo = CompanyInfo()
    collection_names: List[str] = ["esg_reports", "annual_reports"]
    retrievers_: Optional[List[Callable]] = None

    @log_sparse
    def __init__(
            self, 
            collection_names: List[str],
            company_info: CompanyInfo = CompanyInfo(),
            filter_keys: List[str] = ["sedol", "isin", "figi"],
            args_schema: Type[BaseModel] = RetrievalToolSchema,
            **kwargs
            ):
        super().__init__(
            collection_names = collection_names,
            company_info = company_info,
            filter_keys = filter_keys,
            args_schema = args_schema,
            **kwargs
        )
        # self.collection_name = collection_name
        # self.filter_keys = filter_keys
        # self.company_info = company_info
        self._generate_description()

    def _initialize(self):
        """call this before running the tool"""
        filters = self.company_info.as_qdrant_filter()

        indexes = [
            get_index(collection_name=name) 
            for name in self.collection_names
            ]
        # index = get_index(collection_name=self.collection_name)
        self.retrievers_ = [
            index.as_retriever(
                choice_batch_size=10,
                vector_store_kwargs=dict(qdrant_filters=filters)
                )
            for index in indexes
            ]

    @model_validator(mode="before")
    def _set_default_adapter(self):
        return self

    async def _arun(self, **kwargs: RetrievalToolSchema) -> QueryEngineResponse:
        """Use this to query for information in the database. 
        You must pass in a question (str) into the kwarg: question
        :param question: str, the question you want to ask
        """
        # FIXME - seems to trigger error: This was the error: Error code: 403 - {'error': {'code': 'unsupported_country_region_territory', 'message': 'Country, region, or territory not supported', 'param': None, 'type': 'request_forbidden'}}
        results = await arun_queries(
                queries=[get_query(kwargs.get("question"))],
                retrievers=self.retrievers_
            )
        return results
    
    def _run(self, **kwargs: RetrievalToolSchema):
        return asyncio.run(self._arun(**kwargs))
        # if filters:
        #     metadata_filters = MetadataFilters(
        #         filters=filters,
        #         condition=FilterCondition.AND
        #     )
        #     engine = index.as_query_engine(
        #         llm=li_llm,
        #         filters=metadata_filters
        #     )
        # else:
        #     engine = index.as_query_engine(llm=li_llm)
        #     # FIXME

        # # if not question: 
        # # Printer().print(content=f"kwargs: {kwargs}", color="yellow")
        # # Printer().print(content=kwargs.get("question"), color="yellow")
        # question = kwargs.get("question")
        # if question:
        #     context = engine.query(question)
        #     res = QueryEngineResponse(
        #         response=context.response,
        #         sources=context.get_formatted_sources(length=4000)
        #     )
        #     # print(context.response)
        #     return res #context.response
        # else:
            
        #     res = QueryEngineResponse(
        #         response="The query engine has been prepared. However, since you did not "
        #         "pass in a query, I will not return anything. Please pass a query",
        #         sources="None")
        #     return res#.response
        
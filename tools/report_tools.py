from crewai_tools import tool, BaseTool
from pydantic import model_validator, BaseModel
from settings import li_llm, llm
from dbs import get_index, get_query_engine
from data_models import CompanyInfo
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
    FilterCondition
    )
from llama_index.core.tools import (
    QueryEngineTool, 
    ToolMetadata
    )
from typing import List, Dict, Annotated


class QueryEngineSchema(BaseModel):
    question: Annotated[str, "The question you are tring to ask to the database. "]

class QueryEngineResponse(BaseModel):
    response: Annotated[str, "The immediate response"]
    sources: Annotated[str, "The source of the information, converted to string"]

def get_query_engine_tool(
        collection_name: str, 
        company_info: CompanyInfo,
        filter_keys: List[str]=["sedol", "isin", "figi"]
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
    query_tool = QueryEngineTool(
        query_engine=engine,
        metadata=ToolMetadata(
            name="Vector DB Retrieval Tool",
            description=("Tool for retrieving information fromm the vector "
                "store about a particular company. You inputs MUST be a string."),
            fn_schema=QueryEngineSchema
            )
        ).to_langchain_tool()
    return query_tool

class RetrievalTools(BaseTool):
    """Subclassing implementation of the retrieval tool"""
    name: str = "Vector DB Retrieval Tool"
    description: str = "Tool for retrieving information fromm the vector "
    "store about a particular company. You inputs MUST be a string."
    filter_keys: List[str]=["sedol", "isin", "figi"]
    company_info: CompanyInfo
    collection_name: str
    

    @model_validator(mode="before")
    def setup_engine(cls, values):
        # TODO - add support for multiple collections
        company_info = values.get("company_info")
        collection_name = values.get("collection_name")
        if "filter_keys" in values.keys():
            filter_keys = values.get("filter_keys")
        return values

    def _run(self, question: str) -> QueryEngineResponse:
        """Use this to query for information in the database. """
        # FIXME - seems to trigger error: This was the error: Error code: 403 - {'error': {'code': 'unsupported_country_region_territory', 'message': 'Country, region, or territory not supported', 'param': None, 'type': 'request_forbidden'}}
        filters = [
            MetadataFilter(key=key, value=value) 
            for key, value 
            in self.company_info.model_dump().items()
            if (value is not None and key in self.filter_keys)
            ]
        index = get_index(collection=self.collection_name)
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
        if question:
            context = engine.query(question)
            res = QueryEngineResponse(
                response=context.response,
                sources=context.get_formatted_sources(length=4000)
            )
            return res
        else:
            res = QueryEngineResponse(
                response="The query engine has been prepared. However, since you did not "\
                "pass in a query, I will not return anything. Please pass a query",
                sources="None")
            return res
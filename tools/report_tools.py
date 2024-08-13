from crewai_tools import tool, BaseTool
from pydantic import model_validator
from dbs import get_index, get_query_engine
from data_models import CompanyInfo
from llama_index.core.vector_stores import (
    MetadataFilter,
    MetadataFilters,
    FilterOperator,
    FilterCondition
    )

class RetrievalTools(BaseTool):
    name: str = "Vector DB Retrieval Tool"
    description: str = "Tool for retrieving information fromm the vector "
    "store about a particular company."
    company_info: CompanyInfo
    collection_name: str

    @model_validator(mode="before")
    def setup_engine(cls, values):
        # TODO - add support for multiple collections
        company_info = values.get("company_info")
        collection_name = values.get("collection_name")
        filters = [
            MetadataFilter(key=key, value=value) 
            for key, value 
            in company_info.model_dump().items()
            if value is not None
            ]
        index = get_index(collection=collection_name)
        if filters:
            values["filters"] = MetadataFilters(
                filters=[filters],
                condition=FilterCondition.AND
            )
            values["engine"] = index.as_retriever(
                filters=filters
            )
        else:
            values["engine"] = index.as_retriever()
        return values

    def _run(self, question: str):
        """Use this to query for information in the database. """
        # FIXME - seems to trigger error: This was the error: Error code: 403 - {'error': {'code': 'unsupported_country_region_territory', 'message': 'Country, region, or territory not supported', 'param': None, 'type': 'request_forbidden'}}
        if question:
            context = self.engine.query(question)
            return context
        else:
            return "The query engine has been prepared. However, since you did not "\
            "pass in a query, I will not return anything. Please pass a query"
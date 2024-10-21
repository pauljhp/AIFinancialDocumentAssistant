from pydantic import BaseModel
from typing import (
    Optional, List, Sequence, Annotated, 
    Collection, Literal, Dict,
    Hashable, Any)
from enum import Enum
from qdrant_client.http import models
from datetime import datetime


class CompanyInfo(BaseModel):
    """Container representation of a company"""
    composite_figi: Annotated[Optional[str], "Bloomberg FIGI of the company"] = None
    ISIN: Annotated[Optional[str], "ISIN of the company"] = None
    SEDOL: Annotated[Optional[str], "SEDOL of the company"] = None
    short_name: Annotated[Optional[str], "short name of the company"] = None
    name: Annotated[Optional[str], "full name of the company"] = None
    report_year: Annotated[Optional[int], "report year. This is a must have filter"] = 2023
    aliases: Optional[
        Annotated[
            Sequence[str], 
            "Collection of the aliases the company is known as"]
            ] = []
    identifier_fields: List[str] = ["composite_figi", "SEDOL", "ISIN"]

    def __eq__(self, other):
        if self.composite_figi == other.composite_figi or self.ISIN == other.ISIN or self.SEDOL == other.SEDOL:
            return True
        return False
    
    def as_qdrant_filter(self): 
        filter = models.Filter(
            must = [
                models.FieldCondition(
                    key="report_year",
                    match=models.MatchValue(
                        value=self.report_year, 
                    )
                ),
            ],
            should = [
                models.FieldCondition(key=key, match=models.MatchValue(value=getattr(self, key)))
                for key in self.identifier_fields if getattr(self, key)
            ],
            must_not=[
                models.FieldCondition(key="category", match=models.MatchValue(value=v)) 
                for v in ('Title') # prioritize non-title nodes
            ]
        )
        return filter

ESGSection = Literal[
    "corporate_governance",
    "climate_change",
    "edi_hcm",
    "materials_es"
]

ESGPillar = Literal[
    "board_structure",
    "exec_compensation",
    "shareholder_rights",
    "internal_controls",
    "governance_of_sustainability",
    "diversity_in_leadership",
    "workplace_equity",
    "human_capital_management",
    "transition_risk",
    "physical_climate_risk",
    "material_es"
]

class ComputedResults(BaseModel):
    company_info: CompanyInfo
    esg_pillar: ESGPillar
    results: str
    result_source: str #List[Dict[Hashable, Any]] | Dict[Hashable, Any]
    update_date: datetime=datetime.today()


class GetComputedResultsRequest(BaseModel):
    composite_figi: Annotated[Optional[str], "Bloomberg FIGI of the company"] = None
    ISIN: Annotated[Optional[str], "ISIN of the company"] = None
    SEDOL: Annotated[Optional[str], "SEDOL of the company"] = None
    short_name: Annotated[Optional[str], "short name of the company"] = None
    name: Annotated[Optional[str], "full name of the company"] = None
    report_year: Annotated[Optional[int], "report year. This is a must have filter"] = 2023
    aliases: Optional[
        Annotated[
            Sequence[str], 
            "Collection of the aliases the company is known as"]
            ] = []
    identifier_fields: List[str] = ["composite_figi", "SEDOL", "ISIN"]
    # fields above for creating CompanyInfo object
    section: ESGSection
    subsection: ESGPillar
    similarity_top_k: int=10

class ChatRequest(BaseModel):
    session_id: str
    question: str

existing_companies_column_names = Literal[
    "composite_figi",
    "ISIN",
    "SEDOL",
    "report_year",
    "exitsts_in_collection",
    "update_date",
    "collection_name",
    "name"
]

existing_companies_collection_names = Literal[
    "composite_figi",
    "ISIN",
    "SEDOL",
    "report_year",
    "exitsts_in_collection",
    "update_date",
    "collection_name",
    "company name"
]
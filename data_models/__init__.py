from pydantic import BaseModel
from typing import Optional, List, Sequence, Annotated, Collection
from qdrant_client.http import models


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
            ]
        )
        return filter
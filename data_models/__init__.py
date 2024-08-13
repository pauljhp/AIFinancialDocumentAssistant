from pydantic import BaseModel
from typing import Optional, List, Sequence, Annotated, Collection


class CompanyInfo(BaseModel):
    """Container representation of a company"""
    figi: Optional[Annotated[str, "Bloomberg FIGI of the company"]]=None
    isin: Optional[Annotated[str, "ISIN of the company"]]=None
    sedol: Optional[Annotated[str, "SEDOL of the company"]]=None
    short_name: Optional[Annotated[str, "short name of the company"]]=None
    name: Optional[Annotated[str, "full name of the company"]]=None
    aliases: Optional[
        Annotated[
            Sequence[str], 
            "Collection of the aliases the company is known as"]
            ]=None

    def __eq__(self, other):
        if self.figi == other.figi or self.isin == other.isin or self.sedol == other.sedol:
            return True
        return False